import unittest
import math
import time
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai.inference import ai_service
from app.services.detection.mkt import calculate_mkt
from app.services.detection.rate_of_change import RateOfChangeDetector
from app.services.detection.correlation import evaluate_signals
from app.services.routing.engine import SpatialRoutingEngine, CORRIDORS
from app.services.simulation.thermodynamics import ReeferThermodynamicModel
from app.services.simulation.weather import EnvironmentalWeatherEngine
from app.services.simulation.chaos import ChaosIncidentManager
from app.services.audit.merkle import MerkleTree
from app.services.audit.audit_chain import AuditChain
from app.services.iot.gateway import IoTTelemetryGateway


class TestAIService(unittest.TestCase):
    def test_ai_model_readiness(self):
        self.assertTrue(ai_service.is_ready(), "AI Decision Service models failed to load.")

    def test_spoilage_prediction_nominal(self):
        nominal_features = {
            "temperature": 4.2,
            "probe_1_temp": 4.2,
            "probe_2_temp": 4.1,
            "ambient_temperature": 28.0,
            "humidity": 60.0,
            "temp_delta_1h": 0.02
        }
        res = ai_service.predict(nominal_features, temp_ceiling=8.0, temp_floor=2.0)
        self.assertTrue(res["ai_available"])
        self.assertIn("spoilage_probability", res)
        self.assertIn("risk_level", res)
        self.assertIn("forecast", res)
        self.assertIn("top_risk_factors", res)
        self.assertLess(res["spoilage_probability"], 0.70)

    def test_spoilage_prediction_excursion(self):
        breach_features = {
            "temperature": 11.5,
            "probe_1_temp": 11.5,
            "probe_2_temp": 11.4,
            "ambient_temperature": 42.0,
            "humidity": 70.0,
            "temp_delta_1h": 1.2
        }
        res = ai_service.predict(breach_features, temp_ceiling=8.0, temp_floor=2.0)
        self.assertTrue(res["ai_available"])
        self.assertGreater(res["spoilage_probability"], 0.50)
        self.assertIn(res["risk_level"], ["HIGH", "CRITICAL"])
        self.assertTrue(len(res["top_risk_factors"]) > 0)


class TestThermalKinetics(unittest.TestCase):
    def test_mkt_calculation(self):
        # MKT should equal constant temperature if all readings are identical
        temps = [5.0, 5.0, 5.0, 5.0]
        mkt = calculate_mkt(temps)
        self.assertAlmostEqual(mkt, 5.0, places=1)

    def test_mkt_higher_than_mean_under_fluctuation(self):
        # Arrhenius kinetics heavily penalize high temperature excursions
        temps = [4.0, 4.0, 10.0, 4.0]
        mean_temp = sum(temps) / len(temps)
        mkt = calculate_mkt(temps)
        self.assertGreater(mkt, mean_temp)

    def test_roc_calculation(self):
        detector = RateOfChangeDetector(warning_threshold=0.15, critical_threshold=0.30, sustained_duration_seconds=300)
        t1 = datetime(2026, 9, 8, 10, 0, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 9, 8, 10, 10, 0, tzinfo=timezone.utc)
        # Delta 3.5°C in 10 mins = 0.35°C/min -> CRITICAL
        status = detector.check([
            {"timestamp": t1, "temperature": 4.0},
            {"timestamp": t2, "temperature": 7.5}
        ])
        self.assertEqual(status, "CRITICAL")



class TestSpatialRoutingEngine(unittest.TestCase):
    def test_haversine_distance(self):
        # Chennai (13.0827, 80.2707) to Vellore (12.9165, 79.1325) ~125-135 km geodetic
        dist = SpatialRoutingEngine.haversine_km(13.0827, 80.2707, 12.9165, 79.1325)
        self.assertTrue(120.0 < dist < 145.0)

    def test_corridor_spline_generation(self):
        res = SpatialRoutingEngine.generate_corridor_diversion_geometry(
            13.0827, 80.2707, 12.9165, 79.1325, corridor_name="NH-48"
        )
        self.assertEqual(res["source"], "CORRIDOR_TOPOLOGY_SPLINE")
        self.assertGreater(res["distance_km"], 120.0)
        self.assertGreater(res["duration_mins"], 60.0)
        self.assertTrue(len(res["geometry"]) >= 5)

    def test_thermal_feasibility_evaluation(self):
        # Fast ETA (15 min) with nominal temp (4.5°C) -> SAFE
        safe_eval = SpatialRoutingEngine.evaluate_thermal_feasibility(
            eta_mins=15.0,
            current_temp=4.5,
            temp_ceiling=8.0,
            rate_of_change=0.0
        )
        self.assertEqual(safe_eval["status"], "SAFE")
        self.assertTrue(safe_eval["is_feasible"])

        # Active breach (9.5°C) -> BREACH_ACTIVE
        breach_eval = SpatialRoutingEngine.evaluate_thermal_feasibility(
            eta_mins=20.0,
            current_temp=9.5,
            temp_ceiling=8.0,
            rate_of_change=0.2
        )
        self.assertEqual(breach_eval["status"], "BREACH_ACTIVE")


class TestIoTGateway(unittest.TestCase):
    def setUp(self):
        self.gateway = IoTTelemetryGateway()

    def test_sensor_health_nominal(self):
        eff_temp, disc, faults, valid = self.gateway.validate_sensor_health(
            sensor_id="SN-TEST-01",
            probe_1=4.1,
            probe_2=4.2,
            ambient_temp=28.0,
            battery_level=92.0,
            signal_dbm=-65,
            prev_reading=None
        )
        self.assertTrue(valid)
        self.assertAlmostEqual(disc, 0.1, places=2)
        self.assertEqual(len(faults), 0)
        self.assertEqual(eff_temp, 4.2)  # Conservative higher reading

    def test_dual_probe_drift_detection(self):
        # WHO-PQS allowable discrepancy is 1.5°C
        eff_temp, disc, faults, valid = self.gateway.validate_sensor_health(
            sensor_id="SN-TEST-02",
            probe_1=4.0,
            probe_2=6.2,  # 2.2°C drift
            ambient_temp=28.0,
            battery_level=90.0,
            signal_dbm=-65,
            prev_reading=None
        )
        self.assertAlmostEqual(disc, 2.2, places=2)
        fault_codes = [f["fault_code"] for f in faults]
        self.assertIn("DUAL_PROBE_DRIFT", fault_codes)

    def test_circuit_out_of_range(self):
        eff_temp, disc, faults, valid = self.gateway.validate_sensor_health(
            sensor_id="SN-TEST-03",
            probe_1=-999.0,  # Disconnect
            probe_2=None,
            ambient_temp=28.0,
            battery_level=90.0,
            signal_dbm=-65,
            prev_reading=None
        )
        self.assertFalse(valid)
        fault_codes = [f["fault_code"] for f in faults]
        self.assertIn("CIRCUIT_OUT_OF_RANGE", fault_codes)


class TestCryptographicAuditChain(unittest.TestCase):
    def test_merkle_tree_root_and_proof(self):
        leaves = [
            AuditChain.compute_hash(AuditChain.GENESIS_HASH, datetime.now(timezone.utc), "EVT", "SHIP", f"id_{i}", {"seq": i})
            for i in range(8)
        ]
        tree = MerkleTree(leaves)
        root = tree.get_root()
        self.assertEqual(len(root), 64)

        # Test inclusion proof for index 3
        proof = tree.generate_proof(3)
        self.assertIsNotNone(proof)
        self.assertEqual(proof["leaf_hash"], leaves[3])

        # Verify authentic proof
        is_valid = MerkleTree.verify_proof(proof["leaf_hash"], proof["proof_path"], root)
        self.assertTrue(is_valid)

        # Verify forged root rejected
        is_forged = MerkleTree.verify_proof(proof["leaf_hash"], proof["proof_path"], "a" * 64)
        self.assertFalse(is_forged)

    def test_audit_chain_verification_and_tamper(self):
        class MockEvent:
            def __init__(self, eid, prev, ts, etype, ent_type, ent_id, payload, actor="SYSTEM"):
                self.id = eid
                self.previous_hash = prev
                self.timestamp = ts
                self.event_type = etype
                self.entity_type = ent_type
                self.entity_id = ent_id
                self.payload = payload
                self.actor = actor
                self.hash = AuditChain.compute_hash(prev, ts, etype, ent_type, ent_id, payload)

        ts1 = datetime(2026, 9, 8, 12, 0, 0, tzinfo=timezone.utc)
        e1 = MockEvent("e1", AuditChain.GENESIS_HASH, ts1, "DISPATCH", "SHIP", "S1", {"status": "ACTIVE"})
        ts2 = datetime(2026, 9, 8, 12, 5, 0, tzinfo=timezone.utc)
        e2 = MockEvent("e2", e1.hash, ts2, "TELEMETRY", "SENSOR", "SN1", {"temp": 4.2})

        events = [e1, e2]
        verify_res = AuditChain.verify_chain(events)
        self.assertTrue(verify_res["valid"])
        self.assertEqual(verify_res["verified_records"], 2)

        # Adversarial bit-flip tamper simulation
        tamper_res = AuditChain.simulate_tamper(events, target_index=0)
        self.assertTrue(tamper_res["tamper_detected"])
        self.assertFalse(tamper_res["verification_diagnostic"]["valid"])


class TestReeferThermodynamicsAndWeather(unittest.TestCase):
    def test_thermodynamic_cooling(self):
        model = ReeferThermodynamicModel()
        # With normal cooling and warm ambient (35°C), cargo should drop towards setpoint (4.0°C)
        res = model.step(
            dt_seconds=120.0,
            t_current=6.5,
            t_ambient=35.0,
            solar_flux_w_m2=500.0,
            chiller_state="NORMAL",
            door_state="CLOSED",
            target_setpoint=4.0
        )
        self.assertLess(res["t_next"], 6.5)

    def test_thermodynamic_chiller_failure(self):
        model = ReeferThermodynamicModel()
        # With failed chiller, hot ambient (40°C), and open doors, cargo temp must rise
        res = model.step(
            dt_seconds=120.0,
            t_current=4.0,
            t_ambient=40.0,
            solar_flux_w_m2=800.0,
            chiller_state="FAILED",
            door_state="OPEN"
        )
        self.assertGreater(res["t_next"], 4.0)

    def test_weather_engine_diurnal_cycle(self):
        engine = EnvironmentalWeatherEngine()
        # Afternoon 14:00 IST has peak solar and temperature
        noon_utc = datetime(2026, 9, 8, 8, 30, 0, tzinfo=timezone.utc)  # 14:00 IST
        weather_noon = engine.get_weather("NH-48", 13.0, 80.0, timestamp=noon_utc)

        # Night 02:00 IST has zero solar radiation
        night_utc = datetime(2026, 9, 8, 20, 30, 0, tzinfo=timezone.utc)  # 02:00 IST next day
        weather_night = engine.get_weather("NH-48", 13.0, 80.0, timestamp=night_utc)

        self.assertGreater(weather_noon["solar_flux_w_m2"], 600.0)
        self.assertEqual(weather_night["solar_flux_w_m2"], 0.0)
        self.assertGreater(weather_noon["ambient_temperature_c"], weather_night["ambient_temperature_c"])


class TestChaosIncidentManager(unittest.TestCase):
    def test_chaos_injection_and_overrides(self):
        manager = ChaosIncidentManager()
        res = manager.inject_incident("ship_test", "COMPRESSOR_FAILURE", duration_seconds=60)
        self.assertEqual(res["status"], "INJECTED")

        overrides = manager.get_shipment_overrides("ship_test")
        self.assertEqual(overrides["chiller_state"], "FAILED")
        self.assertIn("COMPRESSOR_FAILURE", overrides["active_incident_types"])

        # Clearing chaos restores normal state
        manager.clear_shipment("ship_test")
        overrides_cleared = manager.get_shipment_overrides("ship_test")
        self.assertEqual(overrides_cleared["chiller_state"], "NORMAL")
        self.assertEqual(len(overrides_cleared["active_incident_types"]), 0)


class TestDecisionCorrelation(unittest.TestCase):
    def test_nominal_state(self):
        res = evaluate_signals(
            current_temp=4.2,
            mkt=4.3,
            mkt_limit=8.0,
            temp_max=8.0,
            roc_status="NORMAL",
            door_state="CLOSED",
            speed=55.0,
            ambient_temp=28.0,
            refrigeration_state="NORMAL",
            transit_delay_active=False
        )
        self.assertFalse(res["has_problem"])
        self.assertEqual(res["severity"], "NONE")

    def test_temperature_breach_detection(self):
        res = evaluate_signals(
            current_temp=9.4,
            mkt=7.5,
            mkt_limit=8.0,
            temp_max=8.0,
            roc_status="CRITICAL",
            door_state="CLOSED",
            speed=50.0,
            ambient_temp=38.0,
            refrigeration_state="DEGRADED",
            transit_delay_active=False
        )
        self.assertTrue(res["has_problem"])
        self.assertEqual(res["problem_type"], "temperature_problem")
        self.assertIn(res["severity"], ["HIGH", "CRITICAL"])
        self.assertIn("ai_insights", res)

    def test_door_event_detection(self):
        res = evaluate_signals(
            current_temp=5.0,
            mkt=5.0,
            mkt_limit=8.0,
            temp_max=8.0,
            roc_status="NORMAL",
            door_state="OPEN",
            speed=0.0,
            ambient_temp=37.0,
            refrigeration_state="NORMAL",
            transit_delay_active=False
        )
        self.assertTrue(res["has_problem"])
        self.assertEqual(res["problem_type"], "door_event")


if __name__ == "__main__":
    unittest.main(verbosity=2)

