import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '.')))

from app.core.database import SessionLocal
from app.models.all import Location, Product, Vehicle, Sensor, Shipment, TelemetryReading, Problem, Recommendation, Depot, AuditEvent
from app.services.audit.audit_chain import append_audit_event

def seed_db():
    db = SessionLocal()
    
    # Clean old records
    db.query(AuditEvent).delete()
    db.query(Recommendation).delete()
    db.query(Problem).delete()
    db.query(TelemetryReading).delete()
    db.query(Shipment).delete()
    db.query(Vehicle).delete()
    db.query(Sensor).delete()
    db.query(Depot).delete()
    db.query(Product).delete()
    db.query(Location).delete()
    db.commit()

    now = datetime.now(timezone.utc)

    # 1. Locations
    locations = [
        Location(id="loc_chennai", name="Chennai Regional Vaccine Store", city="Chennai", state="Tamil Nadu", latitude=13.0827, longitude=80.2707, location_type="REGIONAL_STORE"),
        Location(id="loc_vellore", name="Vellore District Hospital Depot", city="Vellore", state="Tamil Nadu", latitude=12.9202, longitude=79.1325, location_type="DISTRICT_STORE"),
        Location(id="loc_delhi", name="National Central Store Delhi", city="Delhi", state="Delhi", latitude=28.6139, longitude=77.2090, location_type="NATIONAL_STORE"),
        Location(id="loc_patna", name="Patna State Medical Store", city="Patna", state="Bihar", latitude=25.5941, longitude=85.1376, location_type="STATE_STORE"),
        Location(id="loc_bengaluru", name="Bengaluru Central Depot", city="Bengaluru", state="Karnataka", latitude=12.9716, longitude=77.5946, location_type="REGIONAL_STORE"),
        Location(id="loc_hyderabad", name="Hyderabad State Cold Store", city="Hyderabad", state="Telangana", latitude=17.3850, longitude=78.4867, location_type="STATE_STORE"),
        Location(id="loc_mumbai", name="Mumbai Western Logistics Hub", city="Mumbai", state="Maharashtra", latitude=19.0760, longitude=72.8777, location_type="REGIONAL_STORE"),
        Location(id="loc_ahmedabad", name="Ahmedabad Civil Store", city="Ahmedabad", state="Gujarat", latitude=23.0225, longitude=72.5714, location_type="DISTRICT_STORE"),
        Location(id="loc_kolkata", name="Kolkata Eastern Depot", city="Kolkata", state="West Bengal", latitude=22.5726, longitude=88.3639, location_type="REGIONAL_STORE"),
        Location(id="loc_guwahati", name="Guwahati Regional Hub", city="Guwahati", state="Assam", latitude=26.1445, longitude=91.7362, location_type="REGIONAL_STORE"),
        Location(id="loc_shillong", name="Shillong Civil Hospital", city="Shillong", state="Meghalaya", latitude=25.5788, longitude=91.8933, location_type="CLINIC"),
    ]
    for loc in locations: db.add(loc)

    # 2. Depots
    depots = [
        Depot(id="depot_kanchi", name="Kanchipuram Backup Store", latitude=12.8341, longitude=79.7036, services=["REFRIGERATION", "VEHICLE_SWAP", "ILR_BUFFER"], availability="HIGH", certification_status="VERIFIED"),
        Depot(id="depot_sriperum", name="Sriperumbudur Medical Hub", latitude=12.9716, longitude=79.9406, services=["REFRIGERATION"], availability="MEDIUM", certification_status="VERIFIED"),
        Depot(id="depot_vellore_sub", name="Vellore Sub-District Depot ILR Room", latitude=12.9165, longitude=79.1320, services=["REFRIGERATION", "DEEP_FREEZE"], availability="HIGH", certification_status="VERIFIED"),
    ]
    for d in depots: db.add(d)

    # 3. Products
    products = [
        Product(id="prod_rotavirus", name="Rotavirus Oral Vaccine (PQS E004)", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_polio", name="Oral Polio Vaccine (OPV) & BCG", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_mr", name="Measles & Rubella Vaccine", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_hepb", name="Hepatitis B & Td", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_penta", name="Pentavalent Vaccine", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_dtp", name="DTP Booster Vaccine", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
    ]
    for p in products: db.add(p)

    # 4. Vehicles & Sensors
    vehicles = [
        Vehicle(id="veh_001", vehicle_code="TX-4821-HX", registration_number="TN-04-E-8841", refrigeration_status="CHILLER_FAULT", current_setpoint=4.0, capacity=4820.0),
        Vehicle(id="veh_002", vehicle_code="DL-01-AK-4420", registration_number="DL-01-AK-4420", refrigeration_status="NORMAL", current_setpoint=4.0, capacity=6000.0),
        Vehicle(id="veh_003", vehicle_code="MH-12-QX-9901", registration_number="MH-12-QX-9901", refrigeration_status="NORMAL", current_setpoint=4.0, capacity=5500.0),
        Vehicle(id="veh_004", vehicle_code="MH-04-AZ-2021", registration_number="MH-04-AZ-2021", refrigeration_status="NORMAL", current_setpoint=4.0, capacity=5000.0),
        Vehicle(id="veh_005", vehicle_code="WB-02-TZ-1120", registration_number="WB-02-TZ-1120", refrigeration_status="NORMAL", current_setpoint=4.0, capacity=3500.0),
        Vehicle(id="veh_006", vehicle_code="AS-01-BK-9182", registration_number="AS-01-BK-9182", refrigeration_status="NORMAL", current_setpoint=4.0, capacity=2500.0),
    ]
    for v in vehicles: db.add(v)

    sensors = [
        Sensor(id=f"sen_10{i}", sensor_code=f"SN-VK10{i}", sensor_type="TEMPERATURE_HUMIDITY_GPS", firmware_version="2.4.1", calibration_status="VALID")
        for i in range(6)
    ]
    for s in sensors: db.add(s)
    db.commit()

    # 5. Shipments
    shipments_data = [
        ("ship_1", "VK-1042", "prod_rotavirus", "loc_chennai", "loc_vellore", "veh_001", "sen_100", "ACTIVE", 9.4, 6.8, "prob_1"),
        ("ship_2", "VK-1047", "prod_polio", "loc_delhi", "loc_patna", "veh_002", "sen_101", "ACTIVE", 7.2, 5.4, "prob_2"),
        ("ship_3", "VK-1039", "prod_mr", "loc_bengaluru", "loc_hyderabad", "veh_003", "sen_102", "ACTIVE", 5.1, 4.3, None),
        ("ship_4", "VK-1045", "prod_hepb", "loc_mumbai", "loc_ahmedabad", "veh_004", "sen_103", "ACTIVE", 4.8, 4.2, None),
        ("ship_5", "VK-1051", "prod_penta", "loc_kolkata", "loc_patna", "veh_005", "sen_104", "ACTIVE", 5.7, 4.9, None),
        ("ship_6", "VK-1033", "prod_dtp", "loc_guwahati", "loc_shillong", "veh_006", "sen_105", "RESOLVED", 4.3, 4.1, None),
    ]

    for sid, scode, pid, oid, did, vid, snid, status, temp, mkt, prob_id in shipments_data:
        sh = Shipment(
            id=sid, shipment_code=scode, product_id=pid, origin_location_id=oid,
            destination_location_id=did, vehicle_id=vid, sensor_id=snid, status=status,
            temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0,
            started_at=now - timedelta(hours=2), estimated_arrival=now + timedelta(hours=2),
            current_temperature=temp, current_mkt=mkt, current_problem_id=prob_id
        )
        db.add(sh)
    db.commit()

    # 6. Problems & Recommendations
    prob1 = Problem(
        id="prob_1", problem_code="PR-1042", shipment_id="ship_1", problem_type="TEMPERATURE_EXCURSION",
        severity="CRITICAL", status="OPEN", detected_at=now - timedelta(minutes=11),
        evidence={"current_temp": 9.4, "threshold": 8.0, "duration_minutes": 11, "location": "Sriperumbudur (Km 38)", "ambient": 38.5, "rate_of_rise": "+0.35°C/min"},
        rule_results={"mkt_breach": True, "sustained_excursion": True, "door_closed": True}
    )
    db.add(prob1)
    rec1 = Recommendation(
        id="rec_1", problem_id="prob_1", rec_type="REROUTE", priority="CRITICAL",
        description="Divert TX-4821-HX to Vellore Sub-District Depot backup cold storage (or Kanchipuram Backup Store)",
        rationale="Chamber temperature 9.4°C exceeds 8.0°C ceiling for 11 min under 38.5°C road temperature. Chiller auxiliary circuit fault flagged.",
        target_depot_id="depot_kanchi", status="PENDING"
    )
    db.add(rec1)

    prob2 = Problem(
        id="prob_2", problem_code="PR-1047", shipment_id="ship_2", problem_type="THERMAL_DRIFT_WARNING",
        severity="MEDIUM", status="ACKNOWLEDGED", detected_at=now - timedelta(minutes=24),
        evidence={"current_temp": 7.2, "threshold": 8.0, "location": "Agra Expressway Toll", "ambient": 41.2},
        rule_results={"rate_of_rise": "+0.12°C/min", "mkt_safe": True}
    )
    db.add(prob2)
    rec2 = Recommendation(
        id="rec_2", problem_id="prob_2", rec_type="CHILLER_OVERRIDE", priority="MEDIUM",
        description="Engage auxiliary refrigeration loop to decrease setpoint to +2.5°C",
        rationale="Approaching 8.0°C ceiling under intense 41.2°C ambient heatwave.",
        target_depot_id="depot_sriperum", status="ACCEPTED"
    )
    db.add(rec2)

    prob3 = Problem(
        id="prob_3", problem_code="PR-1033", shipment_id="ship_6", problem_type="DOOR_SEAL_COMPROMISED",
        severity="LOW", status="RESOLVED", detected_at=now - timedelta(hours=3), resolved_at=now - timedelta(hours=2),
        evidence={"door_state": "SEALED", "duration_open_sec": 45},
        rule_results={"door_reengaged": True, "thermal_delta": "Nominal"}
    )
    db.add(prob3)

    # 7. Telemetry Readings for VK-1042
    temps_1042 = [3.8, 3.9, 4.2, 4.6, 5.4, 6.8, 7.9, 8.4, 9.1, 9.4]
    for idx, t in enumerate(temps_1042):
        t_time = now - timedelta(minutes=(len(temps_1042)-idx)*3)
        tr = TelemetryReading(
            id=f"tel_1042_{idx}", shipment_id="ship_1", timestamp=t_time, temperature=t, humidity=48.0,
            latitude=13.0827 - (idx * 0.015), longitude=80.2707 - (idx * 0.08), speed=54.0,
            door_state="CLOSED", ambient_temperature=38.5, refrigeration_state="FAULT" if t > 8.0 else "NORMAL"
        )
        db.add(tr)
    db.commit()

    # 8. Verifiable Cryptographic Audit Ledger
    append_audit_event(db, "SYSTEM_GENESIS", "SYSTEM", "SYS_001", "SYSTEM", {"message": "VaxKavach Deterministic Cold-Chain Engine Initialized", "standard": "FDA 21 CFR Part 11 / WHO GDP Annex 5"})
    append_audit_event(db, "CONVOY_DISPATCHED", "SHIPMENT", "ship_1", "CHENNAI_DISPATCHER", {"shipment_code": "VK-1042", "origin": "Chennai CWS", "destination": "Vellore Hub", "doses": 8400, "antigen": "Rotavirus"})
    append_audit_event(db, "TELEMETRY_HANDSHAKE", "SENSOR", "sen_100", "IOT_GATEWAY", {"sensor_code": "SN-VK100", "calibration": "NIST-Traceable", "status": "NOMINAL"})
    append_audit_event(db, "THERMAL_EXCURSION_DETECTED", "PROBLEM", "prob_1", "RULE_ENGINE", {"problem_code": "PR-1042", "temperature": 9.4, "mkt": 6.8, "rule": "dT/dt > 0.05 C/min and T > 8.0 C for > 10 min"})
    append_audit_event(db, "RECOMMENDATION_GENERATED", "RECOMMENDATION", "rec_1", "OPERATIONS_ENGINE", {"action": "Divert TX-4821-HX to Kanchipuram Backup Store", "depot_id": "depot_kanchi", "eta_min": 18})
    append_audit_event(db, "DISPATCH_ACKNOWLEDGED", "PROBLEM", "prob_2", "DELHI_OPERATOR", {"problem_code": "PR-1047", "action": "Reefer compressor setpoint adjusted to 2.5C"})
    db.commit()

    db.close()
    print("Seeded database with full realistic VaxKavach operational scenario!")

if __name__ == "__main__":
    seed_db()

