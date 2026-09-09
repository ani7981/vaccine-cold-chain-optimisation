import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.all import Location, Product, Vehicle, Sensor, Shipment, TelemetryReading, Problem, Recommendation, Depot, AuditEvent, TransitEvent, Simulation
from app.services.audit.audit_chain import append_audit_event

def seed_db():
    db = SessionLocal()
    
    # Clean old records cleanly with CASCADE
    try:
        db.execute(text("TRUNCATE TABLE telemetry_readings, transit_events, problems, recommendations, audit_events, simulations, shipments, vehicles, sensors, depots, products, locations CASCADE;"))
        db.commit()
    except Exception:
        db.rollback()
        for model in [Simulation, AuditEvent, Recommendation, Problem, TelemetryReading, TransitEvent, Sensor, Shipment, Vehicle, Depot, Product, Location]:
            try:
                db.query(model).delete(synchronize_session=False)
                db.commit()
            except Exception:
                db.rollback()

    now = datetime.now(timezone.utc)

    # 1. Locations
    locations_data = [
        ("loc_chennai", "Chennai Regional Vaccine Store", "Chennai", "Tamil Nadu", 13.0827, 80.2707, "REGIONAL_STORE"),
        ("loc_vellore", "Vellore District Hospital Depot", "Vellore", "Tamil Nadu", 12.9202, 79.1325, "DISTRICT_STORE"),
        ("loc_delhi", "National Central Store Delhi (GMSD)", "Delhi", "Delhi", 28.6139, 77.2090, "NATIONAL_STORE"),
        ("loc_patna", "Patna State Medical Store", "Patna", "Bihar", 25.5941, 85.1376, "STATE_STORE"),
        ("loc_bengaluru", "Bengaluru Central Facility", "Bengaluru", "Karnataka", 12.9716, 77.5946, "REGIONAL_STORE"),
        ("loc_hyderabad", "Hyderabad State Cold Store", "Hyderabad", "Telangana", 17.3850, 78.4867, "STATE_STORE"),
        ("loc_mumbai", "Mumbai Western Logistics Hub", "Mumbai", "Maharashtra", 19.0760, 72.8777, "REGIONAL_STORE"),
        ("loc_ahmedabad", "Ahmedabad Civil Store", "Ahmedabad", "Gujarat", 23.0225, 72.5714, "DISTRICT_STORE"),
        ("loc_pune", "Pune Zonal Cold Storage", "Pune", "Maharashtra", 18.5204, 73.8567, "DISTRICT_STORE"),
        ("loc_kolkata", "Kolkata Eastern Depot", "Kolkata", "West Bengal", 22.5726, 88.3639, "REGIONAL_STORE"),
        ("loc_guwahati", "Guwahati Regional Hub", "Guwahati", "Assam", 26.1445, 91.7362, "REGIONAL_STORE"),
        ("loc_shillong", "Shillong Civil Hospital", "Shillong", "Meghalaya", 25.5788, 91.8933, "CLINIC"),
        ("loc_agra", "Agra District Health Warehouse", "Agra", "Uttar Pradesh", 27.1767, 78.0081, "DISTRICT_STORE"),
        ("loc_kanpur", "Kanpur Divisional Vaccine Store", "Kanpur", "Uttar Pradesh", 26.4499, 80.3319, "DISTRICT_STORE"),
        ("loc_lucknow", "Lucknow State Vaccine Depot", "Lucknow", "Uttar Pradesh", 26.8467, 80.9462, "STATE_STORE"),
        ("loc_anantapur", "Anantapur District ILR Point", "Anantapur", "Andhra Pradesh", 14.6819, 77.6006, "DISTRICT_STORE"),
        ("loc_kurnool", "Kurnool Medical Depot", "Kurnool", "Andhra Pradesh", 15.8281, 78.0373, "DISTRICT_STORE"),
        ("loc_satara", "Satara District Cold Storage", "Satara", "Maharashtra", 17.6805, 74.0183, "DISTRICT_STORE"),
        ("loc_kolhapur", "Kolhapur Regional Health Store", "Kolhapur", "Maharashtra", 16.7050, 74.2433, "DISTRICT_STORE"),
        ("loc_malda", "Malda Sub-Divisional Store", "Malda", "West Bengal", 25.0108, 88.1411, "DISTRICT_STORE"),
    ]
    for lid, name, city, st, lat, lon, ltype in locations_data:
        loc = Location(
            id=lid, name=name, city=city, state=st, latitude=lat, longitude=lon, location_type=ltype,
            geom=f"SRID=4326;POINT({lon} {lat})"
        )
        db.add(loc)

    # 2. Depots (Backup & Regional Transshipment Hubs across National Corridors)
    depots_data = [
        # NH-48 Southern Corridor (Chennai -> Bengaluru)
        ("depot_sriperum", "Sriperumbudur Medical Hub", 12.9716, 79.9406, ["REFRIGERATION", "ILR_BUFFER"], "HIGH", "VERIFIED"),
        ("depot_kanchi", "Kanchipuram Backup Store", 12.8341, 79.7036, ["REFRIGERATION", "VEHICLE_SWAP", "ILR_BUFFER"], "HIGH", "VERIFIED"),
        ("depot_ranipet", "Ranipet Intermediate Cold Depot", 12.9272, 79.3330, ["REFRIGERATION", "ILR_BUFFER"], "HIGH", "VERIFIED"),
        ("depot_vellore_sub", "Vellore Sub-District Depot ILR Room", 12.9165, 79.1320, ["REFRIGERATION", "DEEP_FREEZE"], "HIGH", "VERIFIED"),
        ("depot_ambur", "Ambur Civil Cold Chain Point", 12.7904, 78.7166, ["REFRIGERATION"], "HIGH", "VERIFIED"),
        ("depot_vaniyambadi", "Vaniyambadi Sub-Depot", 12.6322, 78.4983, ["REFRIGERATION"], "MEDIUM", "VERIFIED"),
        ("depot_krishnagiri", "Krishnagiri District ILR Center", 12.5186, 78.2137, ["REFRIGERATION", "CROSS_DOCKING"], "HIGH", "VERIFIED"),
        ("depot_hosur", "Hosur Inter-State Cross-Dock", 12.7409, 77.8253, ["REFRIGERATION", "VEHICLE_SWAP"], "HIGH", "VERIFIED"),
        ("depot_blr_central", "Bengaluru Central Apex Depot", 12.9716, 77.5946, ["REFRIGERATION", "DEEP_FREEZE", "VEHICLE_SWAP"], "HIGH", "VERIFIED"),
        
        # NH-44 Central Spine (Bengaluru -> Hyderabad)
        ("depot_anantapur", "Anantapur District Health Store", 14.6819, 77.6006, ["REFRIGERATION", "ILR_BUFFER"], "HIGH", "VERIFIED"),
        ("depot_kurnool", "Kurnool Emergency Medical Depot", 15.8281, 78.0373, ["REFRIGERATION", "CROSS_DOCKING"], "HIGH", "VERIFIED"),
        ("depot_hyd_state", "Hyderabad State Apex Cold Facility", 17.3850, 78.4867, ["REFRIGERATION", "DEEP_FREEZE"], "HIGH", "VERIFIED"),

        # NH-19 Northern Arterial (Delhi -> Lucknow)
        ("depot_delhi_apex", "Delhi GMSD National Vaccine Store", 28.6139, 77.2090, ["REFRIGERATION", "DEEP_FREEZE", "VEHICLE_SWAP"], "HIGH", "VERIFIED"),
        ("depot_mathura", "Mathura Highway Emergency ILR", 27.8974, 77.6744, ["REFRIGERATION"], "HIGH", "VERIFIED"),
        ("depot_agra", "Agra Expressway Emergency ILR Bay", 27.1800, 78.0200, ["REFRIGERATION", "CROSS_DOCKING"], "HIGH", "VERIFIED"),
        ("depot_kanpur", "Kanpur Divisional Vaccine Facility", 26.4499, 80.3319, ["REFRIGERATION"], "HIGH", "VERIFIED"),
        ("depot_lucknow_state", "Lucknow Apex State Depot", 26.8467, 80.9462, ["REFRIGERATION", "DEEP_FREEZE"], "HIGH", "VERIFIED"),

        # NH-48 Western Trunk (Mumbai -> Kolhapur)
        ("depot_mum_zonal", "Mumbai Western Zonal Depot", 19.0760, 72.8777, ["REFRIGERATION", "DEEP_FREEZE", "VEHICLE_SWAP"], "HIGH", "VERIFIED"),
        ("depot_lonavala", "Lonavala Expressway Response Point", 18.7546, 73.4062, ["REFRIGERATION"], "HIGH", "VERIFIED"),
        ("depot_pune_zonal", "Pune Zonal Cold Storage", 18.5204, 73.8567, ["REFRIGERATION", "VEHICLE_SWAP"], "HIGH", "VERIFIED"),
        ("depot_satara", "Satara District Health ILR Point", 17.6805, 74.0183, ["REFRIGERATION"], "HIGH", "VERIFIED"),
        ("depot_kolhapur", "Kolhapur Regional Health Facility", 16.7050, 74.2433, ["REFRIGERATION"], "HIGH", "VERIFIED"),

        # NH-106 Northeast Mountain Corridor (Guwahati -> Shillong)
        ("depot_guwahati_hub", "Guwahati Regional Cold Chain Hub", 26.1445, 91.7362, ["REFRIGERATION", "DEEP_FREEZE"], "HIGH", "VERIFIED"),
        ("depot_nongpoh", "Nongpoh Hill Transit Emergency Post", 25.9010, 91.8800, ["REFRIGERATION", "ILR_BUFFER"], "HIGH", "VERIFIED"),
        ("depot_shillong_civ", "Shillong Civil Hospital Cold Room", 25.5788, 91.8933, ["REFRIGERATION"], "HIGH", "VERIFIED"),
    ]
    for did, name, lat, lon, srv, avail, cert in depots_data:
        d = Depot(
            id=did, name=name, latitude=lat, longitude=lon, services=srv, availability=avail,
            certification_status=cert, geom=f"SRID=4326;POINT({lon} {lat})"
        )
        db.add(d)

    # 3. Products (With authentic manufacturers & monographs)
    products = [
        Product(id="prod_rotavirus", name="Rotavirus Oral Vaccine (PQS E004)", manufacturer="Bharat Biotech International Ltd.", doses_per_vial=10, batch_default="BB-ROTA-2026-08", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_mr", name="Measles & Rubella (MR) Vaccine", manufacturer="Serum Institute of India Pvt. Ltd.", doses_per_vial=10, batch_default="SII-MR-2026-11", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_rabies", name="Rabies Human Purified Vero Vaccine", manufacturer="Chiron Behring Vaccines / Bharat Biotech", doses_per_vial=1, batch_default="CB-RAB-2026-03", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_bcg_opv", name="BCG & Bivalent OPV Combo", manufacturer="Serum Institute of India Pvt. Ltd.", doses_per_vial=20, batch_default="SII-BCG-2026-09", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_hepb", name="Hepatitis B Recombinant Vaccine", manufacturer="Biological E. Limited", doses_per_vial=10, batch_default="BE-HEPB-2026-05", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_dpt", name="DTP Adsorbed Booster Vaccine", manufacturer="Panacea Biotec Ltd.", doses_per_vial=10, batch_default="PB-DTP-2026-02", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_ipv", name="Inactivated Polio Vaccine (IPV Fractional)", manufacturer="Sanofi Healthcare India", doses_per_vial=5, batch_default="SAN-IPV-2026-04", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_penta", name="Pentavalent (DTP-HepB-Hib) Vaccine", manufacturer="Serum Institute of India Pvt. Ltd.", doses_per_vial=10, batch_default="SII-PENTA-2026-10", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_je", name="Japanese Encephalitis Live Attenuated (SA 14-14-2)", manufacturer="Wockhardt / CDSCO Quota", doses_per_vial=5, batch_default="WOCK-JE-2026-07", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_td", name="Tetanus and Adult Diphtheria (Td) Toxoid", manufacturer="Biological E. Limited", doses_per_vial=10, batch_default="BE-TD-2026-12", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
        Product(id="prod_covid_boost", name="Corbevax / Protein Subunit Booster", manufacturer="Biological E. Limited", doses_per_vial=20, batch_default="BE-CORB-2026-01", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0),
    ]
    for p in products: db.add(p)

    # 4. 12 Fleet Vehicles (Matching National Corridors & Independent Telemetry)
    vehicles_data = [
        ("veh_001", "VK-1042", "TN-4821-HX", "Tata Ultra Reefer", "K. Muthukrishnan", "+91 94441 20982", "CRITICAL", 12.9675, 79.9427, "NH-48", "CHILLER_FAULT", 4.0, 4820.0),
        ("veh_002", "VK-1047", "DL-01-AB-3301", "BharatBenz 1217C", "R. Sharma", "+91 98110 55821", "WARNING", 27.1767, 78.0081, "NH-19", "HIGH_LOAD", 4.0, 6000.0),
        ("veh_003", "VK-1039", "KA-XX-4521", "Ashok Leyland Boss 1215", "S. Anand", "+91 98450 11203", "HEALTHY", 12.7409, 77.8253, "NH-44", "NORMAL", 4.0, 5500.0),
        ("veh_004", "VK-1045", "MH-XX-8821", "Eicher Pro 3019", "V. Patil", "+91 98200 44901", "HEALTHY", 18.5204, 73.8567, "NH-48-WEST", "NORMAL", 4.0, 5000.0),
        ("veh_005", "VK-1050", "GJ-06-BC-7741", "Tata Ultra T.7", "J. Patel", "+91 98980 66312", "HEALTHY", 22.3072, 73.1812, "NH-48-WEST", "NORMAL", 4.0, 3800.0),
        ("veh_006", "VK-1052", "WB-02-KL-9011", "Ashok Leyland Ecomet", "B. Roy", "+91 98300 77410", "HEALTHY", 25.0108, 88.1411, "NH-19", "NORMAL", 4.0, 4200.0),
        ("veh_007", "VK-1033", "TN-09-CD-1982", "Eicher Pro Reefer", "M. Selvam", "+91 94432 10928", "HEALTHY", 12.9272, 79.3330, "NH-48", "NORMAL", 4.0, 3500.0),
        ("veh_008", "VK-1038", "AP-11-TG-4421", "Tata Prima 2828", "K. Reddy", "+91 98490 22391", "HEALTHY", 15.8281, 78.0373, "NH-44", "NORMAL", 4.0, 7500.0),
        ("veh_009", "VK-1041", "UP-32-BN-8819", "BharatBenz 1617R", "A. Yadav", "+91 94150 99201", "HEALTHY", 26.4499, 80.3319, "NH-19", "NORMAL", 4.0, 5800.0),
        ("veh_010", "VK-1044", "MH-12-PQ-3309", "Mahindra Blazo X", "D. Shinde", "+91 98220 11980", "HEALTHY", 17.6805, 74.0183, "NH-48-WEST", "NORMAL", 4.0, 6200.0),
        ("veh_011", "VK-1048", "KA-04-DE-9102", "Tata Ultra 1014", "N. Gowda", "+91 98440 33812", "HEALTHY", 14.6819, 77.6006, "NH-44", "NORMAL", 4.0, 4500.0),
        ("veh_012", "VK-1055", "AS-01-BK-9182", "Force Traveller Reefer", "P. Barman", "+91 98640 55120", "OFFLINE", 25.8120, 91.8000, "NH-106", "SIGNAL_LOSS", 4.0, 2500.0),
    ]

    for vid, vcode, reg, model, dname, dphone, st, lat, lon, corr, ref_st, sp, cap in vehicles_data:
        v = Vehicle(
            id=vid, vehicle_code=vcode, registration_number=reg, model=model, driver_name=dname,
            driver_phone=dphone, status=st, current_latitude=lat, current_longitude=lon,
            corridor=corr, refrigeration_status=ref_st, current_setpoint=sp, capacity=cap
        )
        db.add(v)

    # 5. Sensors
    for i in range(12):
        s_id = f"sen_1{i:02d}"
        s_code = f"SN-VK{100+i}"
        batt = 88.0 if i == 0 else (92.0 if i == 1 else (42.0 if i == 11 else 95.0 - (i % 5)))
        sig = -72 if i == 11 else -65 + (i % 8)
        last_seen = now - timedelta(minutes=45) if i == 11 else now - timedelta(seconds=12)
        sen = Sensor(
            id=s_id, sensor_code=s_code, sensor_type="TEMPERATURE_HUMIDITY_GPS",
            firmware_version="2.4.1", calibration_status="VALID",
            battery_level=batt, signal_strength_dbm=sig, probe_type="Dual PT100 Class A + SHT31",
            last_seen_at=last_seen
        )
        db.add(sen)
    db.commit()

    # 6. Shipments (12 consignments with complete vaccine details & provenance)
    shipments_data = [
        ("ship_1", "VK-1042", "prod_rotavirus", "loc_chennai", "loc_vellore", "veh_001", "sen_100", "ACTIVE", "BATCH-IND-VR-2026-09", "2027-08-31", 8400, "VERIFIED_OFFICIAL_IOT", False, 9.4, 6.8, "prob_1"),
        ("ship_2", "VK-1047", "prod_mr", "loc_delhi", "loc_patna", "veh_002", "sen_101", "ACTIVE", "BATCH-SII-MR-2026-11", "2027-11-30", 12000, "VERIFIED_OFFICIAL_IOT", False, 7.2, 5.4, "prob_2"),
        ("ship_3", "VK-1039", "prod_rabies", "loc_bengaluru", "loc_hyderabad", "veh_003", "sen_102", "ACTIVE", "BATCH-CB-RAB-2026-03", "2028-02-28", 18000, "VERIFIED_OFFICIAL_IOT", False, 4.2, 4.1, None),
        ("ship_4", "VK-1045", "prod_bcg_opv", "loc_mumbai", "loc_pune", "veh_004", "sen_103", "ACTIVE", "BATCH-SII-BCG-2026-09", "2027-09-30", 15000, "VERIFIED_OFFICIAL_IOT", False, 4.8, 4.2, None),
        ("ship_5", "VK-1050", "prod_hepb", "loc_ahmedabad", "loc_pune", "veh_005", "sen_104", "ACTIVE", "BATCH-BE-HEPB-2026-05", "2027-05-31", 9500, "VERIFIED_OFFICIAL_IOT", False, 3.9, 3.8, None),
        ("ship_6", "VK-1052", "prod_dpt", "loc_kolkata", "loc_malda", "veh_006", "sen_105", "ACTIVE", "BATCH-PB-DTP-2026-02", "2027-03-31", 22000, "VERIFIED_OFFICIAL_IOT", False, 5.1, 4.6, None),
        ("ship_7", "VK-1033", "prod_ipv", "loc_chennai", "loc_vellore", "veh_007", "sen_106", "RESOLVED", "BATCH-SAN-IPV-2026-04", "2027-10-31", 10000, "VERIFIED_OFFICIAL_IOT", False, 4.4, 4.2, "prob_resolved"),
        ("ship_8", "VK-1038", "prod_penta", "loc_kurnool", "loc_hyderabad", "veh_008", "sen_107", "ACTIVE", "BATCH-SII-PV-2026-10", "2027-12-31", 14000, "VERIFIED_OFFICIAL_IOT", False, 4.6, 4.3, None),
        ("ship_9", "VK-1041", "prod_rotavirus", "loc_kanpur", "loc_lucknow", "veh_009", "sen_108", "ACTIVE", "BATCH-BB-RO-2026-08", "2027-07-31", 16500, "VERIFIED_OFFICIAL_IOT", False, 4.9, 4.5, None),
        ("ship_10", "VK-1044", "prod_je", "loc_satara", "loc_kolhapur", "veh_010", "sen_109", "ACTIVE", "BATCH-WOCK-JE-2026-07", "2027-06-30", 8000, "VERIFIED_OFFICIAL_IOT", False, 4.1, 4.0, None),
        ("ship_11", "VK-1048", "prod_td", "loc_bengaluru", "loc_anantapur", "veh_011", "sen_110", "ACTIVE", "BATCH-BE-TD-2026-12", "2028-01-31", 11000, "VERIFIED_OFFICIAL_IOT", False, 4.3, 4.1, None),
        ("ship_12", "VK-1055", "prod_covid_boost", "loc_guwahati", "loc_shillong", "veh_012", "sen_111", "ACTIVE", "BATCH-BE-CORB-2026-01", "2026-12-31", 3200, "SIMULATED_SCENARIO", True, 3.8, 3.7, "prob_3"),
    ]

    for sid, scode, pid, oid, did, vid, snid, st, bnum, exp, doses, prov, is_sim, temp, mkt, prob_id in shipments_data:
        sh = Shipment(
            id=sid, shipment_code=scode, product_id=pid, origin_location_id=oid,
            destination_location_id=did, vehicle_id=vid, sensor_id=snid, status=st,
            batch_number=bnum, expiry_date=exp, doses_count=doses, provenance_source=prov,
            is_simulated=is_sim, temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0,
            started_at=now - timedelta(hours=3), estimated_arrival=now + timedelta(hours=1, minutes=45),
            current_temperature=temp, current_mkt=mkt, current_problem_id=prob_id
        )
        db.add(sh)
    db.commit()

    # 7. Incident Lifecycle: Open -> Investigating -> Action Required -> Resolved
    prob1 = Problem(
        id="prob_1", problem_code="PR-1042", shipment_id="ship_1", problem_type="TEMPERATURE_EXCURSION",
        severity="CRITICAL", status="ACTION_REQUIRED", detected_at=now - timedelta(minutes=14),
        evidence={
            "current_temp": 9.4, "threshold": 8.0, "duration_minutes": 14, "location": "Sriperumbudur (Km 74.2 - NH-48)",
            "ambient": 38.5, "rate_of_rise": "+0.35°C/min", "compressor_rpm": 940, "nominal_rpm": 2200,
            "predictive_risk": {
                "risk_level": "CRITICAL",
                "time_to_breach_minutes": 0,
                "projected_temp_30m": 10.4,
                "explanation": "Active thermal excursion: chamber temperature +1.4°C above 8.0°C ceiling for 14 minutes. Compressor RPM degraded at 940 under 38.5°C road heat.",
                "recommended_action": "Execute immediate diversion to Vellore Sub-District Depot (14 km, 18 min ETA) or Kanchipuram Backup Store."
            }
        },
        rule_results={"mkt_breach": True, "sustained_excursion": True, "door_closed": True, "compressor_fault": True}
    )
    db.add(prob1)
    rec1 = Recommendation(
        id="rec_1", problem_id="prob_1", rec_type="REROUTE", priority="CRITICAL",
        description="Divert TX-4821-HX to Vellore Sub-District Depot backup cold storage (or Kanchipuram Backup Store)",
        rationale="Chamber temperature 9.4°C exceeds 8.0°C ceiling for 14 min under 38.5°C road temperature. Chiller auxiliary circuit fault flagged.",
        target_depot_id="depot_vellore_sub", status="PENDING"
    )
    db.add(rec1)

    prob2 = Problem(
        id="prob_2", problem_code="PR-1047", shipment_id="ship_2", problem_type="PREDICTIVE_THERMAL_DRIFT",
        severity="WARNING", status="INVESTIGATING", detected_at=now - timedelta(minutes=22),
        evidence={
            "current_temp": 7.2, "threshold": 8.0, "location": "Agra Expressway Km 118", "ambient": 41.2,
            "rate_of_rise": "+0.18°C/min", "compressor_rpm": 2100,
            "predictive_risk": {
                "risk_level": "HIGH",
                "time_to_breach_minutes": 14,
                "projected_temp_30m": 8.5,
                "explanation": "Temperature climbing at +0.18°C/min under extreme 41.2°C ambient heatwave. Projected upper ceiling breach in ~14 minutes.",
                "recommended_action": "Engage secondary inverter loop and lower compressor setpoint to +2.5°C before ceiling breach."
            }
        },
        rule_results={"rate_of_rise": "+0.18°C/min", "mkt_safe": True, "trend_critical": True}
    )
    db.add(prob2)
    rec2 = Recommendation(
        id="rec_2", problem_id="prob_2", rec_type="CHILLER_OVERRIDE", priority="MEDIUM",
        description="Engage auxiliary refrigeration loop to decrease setpoint to +2.5°C",
        rationale="Approaching 8.0°C ceiling under intense 41.2°C ambient heatwave.",
        target_depot_id="depot_agra", status="ACCEPTED"
    )
    db.add(rec2)

    prob3 = Problem(
        id="prob_3", problem_code="PR-1055", shipment_id="ship_12", problem_type="SIGNAL_LOSS_OFFLINE",
        severity="WARNING", status="OPEN", detected_at=now - timedelta(minutes=45),
        evidence={
            "last_known_temp": 3.8, "location": "Meghalaya Ghat Corridor (Km 42)", "duration_offline_min": 45,
            "predictive_risk": {
                "risk_level": "MODERATE",
                "time_to_breach_minutes": None,
                "explanation": "Cellular telemetry link dropped in mountain terrain. Vehicle battery at 42%. Thermal buffer estimated at 3.5 hours.",
                "recommended_action": "Attempt radio contact with driver P. Barman (+91 98640 55120) or dispatch checkpost alert at Nongpoh."
            }
        },
        rule_results={"heartbeat_missing": True, "battery_warning": True}
    )
    db.add(prob3)

    # Resolved Problem with full documented resolution parameters
    prob_resolved = Problem(
        id="prob_resolved", problem_code="PR-1033", shipment_id="ship_7", problem_type="DOOR_SEAL_COMPROMISED",
        severity="LOW", status="RESOLVED", detected_at=now - timedelta(hours=3), resolved_at=now - timedelta(hours=1, minutes=30),
        resolution_reason="Secondary door latch seal disengaged during highway toll inspection.",
        corrective_action="Driver inspected door gasket, re-engaged dual cam-lock, and confirmed chamber temperature dropped to +4.4°C.",
        resolution_notes="Operator verified temperature recovery within 12 minutes. Biological integrity intact.",
        resolved_by_user="DISPATCH_SUPERVISOR_CHENNAI",
        evidence={"door_state": "SEALED", "duration_open_sec": 45, "thermal_recovery": "+4.4°C"},
        rule_results={"door_reengaged": True, "thermal_delta": "Nominal"}
    )
    db.add(prob_resolved)

    # 8. Detailed Telemetry Readings for active consignments
    temps_1042 = [3.8, 3.9, 4.2, 4.6, 5.4, 6.8, 7.9, 8.4, 9.1, 9.4]
    for idx, t in enumerate(temps_1042):
        t_time = now - timedelta(minutes=(len(temps_1042)-idx)*3)
        tr = TelemetryReading(
            id=f"tel_1042_{idx}", shipment_id="ship_1", timestamp=t_time, temperature=t, humidity=48.0,
            latitude=13.0827 - (idx * 0.015), longitude=80.2707 - (idx * 0.08), speed=62.0,
            door_state="CLOSED", ambient_temperature=38.5, refrigeration_state="FAULT" if t > 8.0 else "NORMAL"
        )
        db.add(tr)

    temps_1047 = [4.5, 4.8, 5.2, 5.7, 6.2, 6.6, 6.9, 7.2]
    for idx, t in enumerate(temps_1047):
        t_time = now - timedelta(minutes=(len(temps_1047)-idx)*4)
        tr = TelemetryReading(
            id=f"tel_1047_{idx}", shipment_id="ship_2", timestamp=t_time, temperature=t, humidity=42.0,
            latitude=28.6139 - (idx * 0.18), longitude=77.2090 + (idx * 0.10), speed=74.0,
            door_state="CLOSED", ambient_temperature=41.2, refrigeration_state="HIGH_LOAD"
        )
        db.add(tr)

    temps_1039 = [4.1, 4.2, 4.3, 4.2, 4.2, 4.3, 4.2]
    for idx, t in enumerate(temps_1039):
        t_time = now - timedelta(minutes=(len(temps_1039)-idx)*5)
        tr = TelemetryReading(
            id=f"tel_1039_{idx}", shipment_id="ship_3", timestamp=t_time, temperature=t, humidity=50.0,
            latitude=12.9716 + (idx * 0.08), longitude=77.5946 + (idx * 0.12), speed=58.0,
            door_state="CLOSED", ambient_temperature=33.0, refrigeration_state="NORMAL"
        )
        db.add(tr)

    db.commit()

    # 9. Verifiable Cryptographic Audit Ledger (SHA-256 Chained)
    append_audit_event(db, "SYSTEM_GENESIS", "SYSTEM", "SYS_001", "SYSTEM", {"message": "VaxKavach Deterministic Cold-Chain Engine Initialized", "standard": "FDA 21 CFR Part 11 / WHO GDP Annex 5"})
    append_audit_event(db, "CONVOY_DISPATCHED", "SHIPMENT", "ship_1", "CHENNAI_DISPATCHER", {"shipment_code": "VK-1042", "origin": "Chennai Regional Vaccine Store", "destination": "Vellore Hub", "doses": 8400, "antigen": "Rotavirus"})
    append_audit_event(db, "TELEMETRY_HANDSHAKE", "SENSOR", "sen_100", "IOT_GATEWAY", {"sensor_code": "SN-VK100", "calibration": "NIST-Traceable", "status": "NOMINAL"})
    append_audit_event(db, "THERMAL_EXCURSION_DETECTED", "PROBLEM", "prob_1", "RULE_ENGINE", {"problem_code": "PR-1042", "temperature": 9.4, "mkt": 6.8, "rule": "dT/dt > 0.05 C/min and T > 8.0 C for > 10 min"})
    append_audit_event(db, "RECOMMENDATION_GENERATED", "RECOMMENDATION", "rec_1", "OPERATIONS_ENGINE", {"action": "Divert TX-4821-HX to Vellore Sub-District Depot", "depot_id": "depot_vellore_sub", "eta_min": 18})
    append_audit_event(db, "PREDICTIVE_BREACH_ALERT", "PROBLEM", "prob_2", "AI_RISK_ENGINE", {"problem_code": "PR-1047", "current_temp": 7.2, "predicted_breach_mins": 14, "cause": "Rate of rise +0.18C/min under 41.2C ambient"})
    append_audit_event(db, "INCIDENT_RESOLVED", "PROBLEM", "prob_resolved", "DISPATCH_SUPERVISOR_CHENNAI", {"problem_code": "PR-1033", "reason": "Secondary door latch seal disengaged", "action": "Driver resealed cam-lock; thermal stability recovered to +4.4C", "verified_by": "SUPERVISOR_CHENNAI"})
    db.commit()

    db.close()
    print("Seeded database with full 12-vehicle national fleet and verified audit ledger!")

if __name__ == "__main__":
    seed_db()

