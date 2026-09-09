import asyncio
import logging
import math
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.all import Simulation, Shipment, Vehicle, TelemetryReading, Recommendation, Problem
from app.services.routing.engine import CORRIDORS
from app.services.simulation.thermodynamics import ReeferThermodynamicModel
from app.services.simulation.weather import EnvironmentalWeatherEngine
from app.services.simulation.chaos import chaos_manager, ChaosIncidentManager
from app.services.iot.gateway import iot_gateway
from app.websocket.manager import manager

logger = logging.getLogger("simulation_engine")

class CorridorNavigator:
    """Computes smooth, uniform-speed waypoint interpolation along highway corridors."""

    def __init__(self, waypoints: List[Tuple[float, float]]):
        self.waypoints = waypoints
        self.segments: List[float] = []
        self.cumulative_dist: List[float] = [0.0]
        self._calculate_distances()

    def _haversine_km(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2.0)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return 6371.0 * c

    def _calculate_distances(self):
        total = 0.0
        for i in range(len(self.waypoints) - 1):
            dist = self._haversine_km(self.waypoints[i], self.waypoints[i + 1])
            self.segments.append(dist)
            total += dist
            self.cumulative_dist.append(total)
        self.total_distance_km = max(0.1, total)

    def interpolate(self, progress: float) -> Tuple[float, float]:
        """Progress clamped between 0.0 (origin) and 1.0 (destination)."""
        p = max(0.0, min(1.0, progress))
        target_km = p * self.total_distance_km

        if p <= 0.0:
            return self.waypoints[0]
        if p >= 1.0:
            return self.waypoints[-1]

        # Find segment
        for i in range(len(self.segments)):
            if self.cumulative_dist[i] <= target_km <= self.cumulative_dist[i + 1]:
                seg_len = self.segments[i]
                if seg_len == 0.0:
                    return self.waypoints[i]
                fraction = (target_km - self.cumulative_dist[i]) / seg_len
                lat1, lon1 = self.waypoints[i]
                lat2, lon2 = self.waypoints[i + 1]
                lat = lat1 + fraction * (lat2 - lat1)
                lon = lon1 + fraction * (lon2 - lon1)
                return (round(lat, 6), round(lon, 6))

        return self.waypoints[-1]


class SimulationEngine:
    """
    Real-Time Dynamic Simulation & Stochastic Environmental Weather Engine:
    - First-Principles Newton-Fourier Thermodynamic Heat Transfer Model.
    - Diurnal Solar Radiation & Regional Corridor Microclimate Engine.
    - Multi-Corridor Concurrent Convoy Fleet Movement.
    - Adversarial Real-Time Chaos & Incident Injection.
    - Full end-to-end integration through the Industrial IoT Ingestion Gateway.
    """

    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.weather_engine = EnvironmentalWeatherEngine()
        self.chaos_manager = chaos_manager
        
        # State caches per shipment
        self.thermo_models: Dict[str, ReeferThermodynamicModel] = {}
        self.navigators: Dict[str, CorridorNavigator] = {}
        self.convoy_progress: Dict[str, float] = {}
        self.convoy_temperatures: Dict[str, float] = {}
        self.sequence_counters: Dict[str, int] = {}
        self.tick_interval_seconds = 2.0  # Real-time cadence
        self.sim_dt_seconds = 120.0       # Simulated transit time advanced per tick (2 minutes)
        self.current_tick = 0
        self.sim_start_time = datetime.now(timezone.utc)

    def _init_shipment_state(self, db: Session, shipment: Shipment):
        s_id = shipment.id
        if s_id not in self.thermo_models:
            self.thermo_models[s_id] = ReeferThermodynamicModel()

        if s_id not in self.convoy_progress:
            self.convoy_progress[s_id] = 0.05  # Start 5% into route

        if s_id not in self.convoy_temperatures:
            self.convoy_temperatures[s_id] = shipment.current_temperature or 4.0

        if s_id not in self.sequence_counters:
            self.sequence_counters[s_id] = 100

        # Corridor Navigation
        vehicle = db.query(Vehicle).filter(Vehicle.id == shipment.vehicle_id).first() if shipment.vehicle_id else None
        corridor_code = (vehicle.corridor if vehicle and vehicle.corridor else "NH-48").upper()
        if corridor_code not in CORRIDORS:
            corridor_code = "NH-48"

        if s_id not in self.navigators:
            waypoints = CORRIDORS[corridor_code]["waypoints"]
            self.navigators[s_id] = CorridorNavigator(waypoints)

    def start(self, db: Session, scenario: str = "pan_india_dynamic"):
        if self.task and not self.task.done():
            self.task.cancel()

        sim = db.query(Simulation).first()
        if not sim:
            sim = Simulation(scenario=scenario, status="RUNNING", speed_multiplier=1.0)
            db.add(sim)
        else:
            sim.status = "RUNNING"
            sim.scenario = scenario
            sim.current_tick = 0

        db.commit()

        self.is_running = True
        self.current_tick = 0
        self.sim_start_time = datetime.now(timezone.utc)
        self.task = asyncio.create_task(self._simulation_loop())
        logger.info(f"Simulation Engine launched in background (scenario: {scenario})")

    def stop(self, db: Session):
        self.is_running = False
        if self.task and not self.task.done():
            self.task.cancel()
        sim = db.query(Simulation).first()
        if sim:
            sim.status = "STOPPED"
            db.commit()
        logger.info("Simulation Engine halted.")

    def inject_chaos(self, shipment_id: str, incident_type: str, duration_seconds: int = 300) -> Dict[str, Any]:
        return self.chaos_manager.inject_incident(shipment_id, incident_type, duration_seconds)

    def clear_chaos(self, shipment_id: Optional[str] = None):
        if shipment_id:
            self.chaos_manager.clear_shipment(shipment_id)
        else:
            self.chaos_manager.clear_all()

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "current_tick": self.current_tick,
            "sim_dt_seconds_per_tick": self.sim_dt_seconds,
            "sim_time": (self.sim_start_time + timedelta(seconds=self.current_tick * self.sim_dt_seconds)).isoformat(),
            "active_convoys": [
                {
                    "shipment_id": s_id,
                    "progress_percent": round(prog * 100.0, 1),
                    "compartment_temp_c": round(self.convoy_temperatures.get(s_id, 4.0), 2)
                }
                for s_id, prog in self.convoy_progress.items()
            ],
            "active_chaos_incidents": self.chaos_manager.get_all_active()
        }

    async def _simulation_loop(self):
        while self.is_running:
            db = SessionLocal()
            try:
                sim = db.query(Simulation).first()
                if not sim or sim.status != "RUNNING":
                    self.is_running = False
                    break

                # Query active shipments
                active_shipments = db.query(Shipment).filter(Shipment.status.in_(["ACTIVE", "IN_TRANSIT"])).all()
                if not active_shipments:
                    active_shipments = db.query(Shipment).limit(4).all()

                sim_time = self.sim_start_time + timedelta(seconds=self.current_tick * self.sim_dt_seconds)

                for shipment in active_shipments:
                    s_id = shipment.id
                    self._init_shipment_state(db, shipment)

                    # Retrieve physical overrides from Chaos Manager
                    overrides = self.chaos_manager.get_shipment_overrides(s_id)
                    chiller_state = overrides["chiller_state"]
                    door_state = overrides["door_state"]
                    probe_drift = overrides["probe_drift_delta"]
                    heatwave_active = overrides["heatwave_active"]

                    # Check DB for active unresolved problem affecting refrigeration
                    if chiller_state == "NORMAL" and shipment.current_problem_id:
                        active_prob = db.query(Problem).filter(
                            Problem.id == shipment.current_problem_id,
                            Problem.status.in_(["OPEN", "IN_PROGRESS", "ACTION_REQUIRED", "ACKNOWLEDGED", "INVESTIGATING"])
                        ).first()
                        if active_prob:
                            prob_type = (active_prob.problem_type or "").upper()
                            if prob_type in ["TEMPERATURE_EXCURSION", "REFRIGERATION_FAILURE", "COMPRESSOR_FAILURE"]:
                                chiller_state = "FAILED"
                            elif prob_type in ["PREDICTIVE_THERMAL_DRIFT"]:
                                chiller_state = "DEGRADED"
                            elif prob_type in ["DOOR_AJAR", "DOOR_SEAL_COMPROMISED"]:
                                door_state = "OPEN"

                    # 1. Update Vehicle Position & Spatial Progress
                    nav = self.navigators[s_id]
                    vehicle = db.query(Vehicle).filter(Vehicle.id == shipment.vehicle_id).first() if shipment.vehicle_id else None
                    corridor_code = (vehicle.corridor if vehicle and vehicle.corridor else "NH-48").upper()
                    if corridor_code not in CORRIDORS:
                        corridor_code = "NH-48"

                    nominal_speed = CORRIDORS[corridor_code]["nominal_speed_kmh"]
                    actual_speed = overrides["speed_override"] if overrides["speed_override"] is not None else max(30.0, nominal_speed + random.gauss(0.0, 4.0))

                    # Progress advance
                    dist_advanced_km = (actual_speed * (self.sim_dt_seconds / 3600.0))
                    delta_progress = dist_advanced_km / nav.total_distance_km
                    new_progress = min(1.0, self.convoy_progress[s_id] + delta_progress)
                    # Loop back or complete
                    if new_progress >= 1.0:
                        new_progress = 0.05
                    self.convoy_progress[s_id] = new_progress

                    lat, lon = nav.interpolate(new_progress)

                    # Update vehicle live coordinates in DB
                    if vehicle:
                        vehicle.current_latitude = lat
                        vehicle.current_longitude = lon

                    # 2. Compute Atmospheric Weather
                    weather = self.weather_engine.get_weather(
                        corridor=corridor_code,
                        lat=lat,
                        lon=lon,
                        timestamp=sim_time,
                        chaos_heatwave=heatwave_active
                    )

                    # 3. Step Thermodynamic Model
                    current_temp = self.convoy_temperatures[s_id]
                    thermo_res = self.thermo_models[s_id].step(
                        dt_seconds=self.sim_dt_seconds,
                        t_current=current_temp,
                        t_ambient=weather["ambient_temperature_c"],
                        solar_flux_w_m2=weather["solar_flux_w_m2"],
                        chiller_state=chiller_state,
                        door_state=door_state,
                        target_setpoint=4.0
                    )
                    next_temp = thermo_res["t_next"]
                    self.convoy_temperatures[s_id] = next_temp

                    # 4. Generate Dual-Probe Readings
                    # Probe 1 has minor measurement jitter
                    probe_1_temp = round(next_temp + random.gauss(0.0, 0.04), 2)
                    # Probe 2 tracks Probe 1 closely unless probe drift chaos is active
                    probe_2_temp = round(next_temp + probe_drift + random.gauss(0.0, 0.04), 2)

                    # 5. Build IoT Telemetry Packet
                    self.sequence_counters[s_id] += 1
                    packet = {
                        "shipment_id": s_id,
                        "shipment_code": shipment.shipment_code,
                        "timestamp": sim_time.isoformat(),
                        "sequence_number": self.sequence_counters[s_id],
                        "temperature": probe_1_temp,
                        "probe_1_temperature": probe_1_temp,
                        "probe_2_temperature": probe_2_temp,
                        "ambient_temperature": weather["ambient_temperature_c"],
                        "humidity": weather["humidity_percent"],
                        "latitude": lat,
                        "longitude": lon,
                        "speed": round(actual_speed, 1),
                        "door_state": door_state,
                        "refrigeration_state": chiller_state,
                        "battery_level": round(max(10.0, 96.0 - (self.current_tick * 0.02)), 1),
                        "signal_strength_dbm": -68 if actual_speed > 0 else -82
                    }

                    # 6. Ingest into Industrial IoT Gateway (dedup, diagnostics, Arrhenius kinetics, detection, routing)
                    try:
                        ingest_res = iot_gateway.ingest_packet(db, packet)

                        # Broadcast real-time telemetry to all connected cockpit/HUD clients
                        await manager.broadcast({
                            "type": "TELEMETRY_UPDATE",
                            "payload": {
                                "shipment_id": s_id,
                                "shipment_code": shipment.shipment_code,
                                "temperature": probe_1_temp,
                                "probe_1": probe_1_temp,
                                "probe_2": probe_2_temp,
                                "mkt": shipment.current_mkt or probe_1_temp,
                                "ambient_temperature": weather["ambient_temperature_c"],
                                "humidity": weather["humidity_percent"],
                                "latitude": lat,
                                "longitude": lon,
                                "lat": lat,
                                "lon": lon,
                                "speed": round(actual_speed, 1),
                                "door_state": door_state,
                                "refrigeration_state": chiller_state,
                                "battery_level": packet["battery_level"],
                                "signal_strength_dbm": packet["signal_strength_dbm"],
                                "progress_percent": round(self.convoy_progress[s_id] * 100.0, 1),
                                "corridor": corridor_code,
                                "tick": self.current_tick,
                                "timestamp": sim_time.isoformat(),
                                "has_problem": ingest_res.get("decision", {}).get("has_problem", False),
                                "severity": ingest_res.get("decision", {}).get("severity", "LOW")
                            }
                        })

                        # If a problem was detected, broadcast urgent dispatch alert
                        created_problem = ingest_res.get("created_problem")
                        if created_problem:
                            prob_id = created_problem["id"] if isinstance(created_problem, dict) else created_problem.id
                            prob_code = created_problem.get("code", getattr(created_problem, "problem_code", "")) if isinstance(created_problem, dict) else created_problem.problem_code
                            prob_type = created_problem.get("type", getattr(created_problem, "problem_type", "")) if isinstance(created_problem, dict) else created_problem.problem_type
                            prob_sev = created_problem.get("severity", getattr(created_problem, "severity", "")) if isinstance(created_problem, dict) else created_problem.severity
                            rec = db.query(Recommendation).filter(Recommendation.problem_id == prob_id).first()
                            await manager.broadcast({
                                "type": "PROBLEM_RAISED",
                                "payload": {
                                    "problem_id": prob_id,
                                    "problem_code": prob_code,
                                    "shipment_id": shipment.id,
                                    "shipment_code": shipment.shipment_code,
                                    "problem_type": prob_type,
                                    "severity": prob_sev,
                                    "temperature": probe_1_temp,
                                    "lat": lat,
                                    "lon": lon,
                                    "recommendation": {
                                        "id": rec.id if rec else None,
                                        "description": rec.description if rec else "Divert to accredited depot",
                                        "rationale": rec.rationale if rec else "Prevent thermal excursion",
                                        "target_depot_id": rec.target_depot_id if rec else None
                                    }
                                }
                            })
                    except Exception as ingest_err:
                        logger.error(f"IoT Ingestion error on {s_id}: {ingest_err}")

                sim.current_tick = self.current_tick
                sim.simulation_time = sim_time
                db.commit()

                self.current_tick += 1

            except Exception as e:
                logger.error(f"Simulation loop tick error: {e}", exc_info=True)
            finally:
                db.close()

            await asyncio.sleep(self.tick_interval_seconds)

simulation_engine = SimulationEngine()
