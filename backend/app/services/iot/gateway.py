import math
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.all import Shipment, TelemetryReading, Vehicle, Sensor, Problem, Recommendation
from app.services.detection.correlation import evaluate_signals
from app.services.detection.mkt import calculate_mkt
from app.services.audit.audit_chain import append_audit_event
from app.services.routing.engine import spatial_routing_engine

logger = logging.getLogger("iot_gateway")

class IoTTelemetryGateway:
    """
    Industrial-Grade Cold-Chain Telemetry Ingestion Gateway:
    1. Packet Deduplication via sliding sequence memory.
    2. Out-of-Order Jitter Reconciliation & Chronological Reassembly.
    3. Multi-Sensor Fault & Dual-Probe Drift Diagnostic Pipeline (WHO-PQS E004).
    4. Real-Time Arrhenius Kinetics & Hybrid 4-Tier Evaluation.
    """

    def __init__(self):
        # Sliding cache for deduplication: key -> (arrival_time, result)
        self._seen_packets: Dict[str, datetime] = {}
        # Sensor historical probe variance tracking: sensor_id -> list of recent temps
        self._probe_history: Dict[str, List[Tuple[float, float, float]]] = {}  # (t1, t2, ambient)

    def _cleanup_old_cache(self, max_age_seconds: int = 3600):
        now = datetime.now(timezone.utc)
        keys_to_del = [k for k, t in self._seen_packets.items() if (now - t).total_seconds() > max_age_seconds]
        for k in keys_to_del:
            del self._seen_packets[k]

    def validate_sensor_health(
        self,
        sensor_id: str,
        probe_1: float,
        probe_2: Optional[float],
        ambient_temp: float,
        battery_level: Optional[float],
        signal_dbm: Optional[int],
        prev_reading: Optional[TelemetryReading]
    ) -> Tuple[float, float, List[Dict[str, Any]], bool]:
        """
        Diagnoses sensor integrity according to WHO-PQS E004 & EN 12830 standards:
        - Dual-probe divergence / drift
        - Frozen/stuck sensor lockup
        - Open-circuit electrical spike
        - Battery exhaustion & signal degradation
        Returns: (effective_temp, probe_discrepancy, fault_flags, is_valid)
        """
        faults = []
        is_valid = True

        # 1. Dual-Probe Cross-Validation (consensus vs discrepancy)
        if probe_2 is not None:
            probe_discrepancy = round(abs(probe_1 - probe_2), 3)
            # WHO-PQS E004 max allowable inter-probe discrepancy is 1.5°C
            if probe_discrepancy > 1.5:
                faults.append({
                    "fault_code": "DUAL_PROBE_DRIFT",
                    "severity": "WARNING" if probe_discrepancy < 3.0 else "CRITICAL",
                    "detail": f"Inter-probe discrepancy ({probe_discrepancy:.2f}°C) exceeds allowable tolerance (1.50°C). Possible sensor calibration drift or compartment temperature stratification."
                })
            # Fail-safe temperature selection: for spoilage prevention, take the more conservative (higher) value
            effective_temp = max(probe_1, probe_2)
        else:
            probe_discrepancy = 0.0
            effective_temp = probe_1

        # 2. Out-of-Range / Circuit Disconnect Check
        if effective_temp < -90.0 or effective_temp > 60.0 or math.isnan(effective_temp):
            faults.append({
                "fault_code": "CIRCUIT_OUT_OF_RANGE",
                "severity": "CRITICAL",
                "detail": f"Raw probe reading ({effective_temp}°C) outside physical sensor envelope [-90°C, +60°C]. Probable open-circuit wire fault or loose terminal."
            })
            is_valid = False
            effective_temp = prev_reading.temperature if prev_reading else 4.0

        # 3. Electrical Spike / Rapid Disconnect Detection
        if prev_reading and prev_reading.temperature is not None:
            temp_step = abs(effective_temp - prev_reading.temperature)
            # In a heavy thermal shipper, payload temperature cannot physically jump >6°C in a single ping interval
            if temp_step > 6.0:
                faults.append({
                    "fault_code": "THERMAL_SPIKE_ANOMALY",
                    "severity": "WARNING",
                    "detail": f"Unrealistic instantaneous temperature step (ΔT = {temp_step:.2f}°C). Verifying latch and thermal probe ground."
                })

        # 4. Stuck / Frozen Sensor Detection (ADC Lockup)
        # Check if last 6 readings had identically zero variance despite ambient variation
        if sensor_id not in self._probe_history:
            self._probe_history[sensor_id] = []
        
        hist = self._probe_history[sensor_id]
        hist.append((probe_1, probe_2 if probe_2 is not None else probe_1, ambient_temp))
        if len(hist) > 8:
            hist.pop(0)

        if len(hist) >= 6:
            p1_vals = [h[0] for h in hist]
            amb_vals = [h[2] for h in hist]
            p1_variance = max(p1_vals) - min(p1_vals)
            amb_variance = max(amb_vals) - min(amb_vals)
            
            # If payload probe has exactly 0.000 variance while ambient air changed by > 2.0°C
            if p1_variance == 0.0 and amb_variance > 2.0:
                faults.append({
                    "fault_code": "FROZEN_PROBE_LOCKUP",
                    "severity": "HIGH",
                    "detail": "Probe reported static reading (0.00°C variance) across 6 consecutive pings while ambient air fluctuated. Sensor ADC or simulator output may be locked."
                })

        # 5. Battery and Signal Integrity
        if battery_level is not None and battery_level < 15.0:
            faults.append({
                "fault_code": "BATTERY_CRITICAL",
                "severity": "WARNING" if battery_level > 8.0 else "CRITICAL",
                "detail": f"Logger reserve battery critically low ({battery_level:.1f}%). Replace telemetry pack at next cross-dock."
            })

        if signal_dbm is not None and signal_dbm < -105:
            faults.append({
                "fault_code": "CELLULAR_SIGNAL_DEGRADED",
                "severity": "LOW",
                "detail": f"Cellular RSSI degraded ({signal_dbm} dBm). Transit through fringe coverage corridor."
            })

        return effective_temp, probe_discrepancy, faults, is_valid

    def ingest_packet(self, db: Session, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single raw IoT telemetry packet with complete deduplication,
        sensor diagnostics, kinetic updates, and hybrid problem detection.
        """
        # 1. Identify Target Shipment
        shipment_id = packet.get("shipment_id")
        shipment = None
        if shipment_id:
            shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        
        # Fallback to lookup by shipment_code or vehicle
        if not shipment and packet.get("shipment_code"):
            shipment = db.query(Shipment).filter(Shipment.shipment_code == packet.get("shipment_code")).first()
        if not shipment and packet.get("vehicle_code"):
            veh = db.query(Vehicle).filter(Vehicle.vehicle_code == packet.get("vehicle_code")).first()
            if veh:
                shipment = db.query(Shipment).filter(Shipment.vehicle_id == veh.id).first()

        if not shipment:
            return {"status": "error", "error_code": "SHIPMENT_NOT_FOUND", "detail": f"Could not correlate packet to active shipment: {packet}"}

        # 2. Parse & Standardize Timestamp
        raw_ts = packet.get("timestamp")
        if not raw_ts:
            dt = datetime.now(timezone.utc)
        elif isinstance(raw_ts, (int, float)):
            dt = datetime.fromtimestamp(raw_ts, tz=timezone.utc)
        elif isinstance(raw_ts, str):
            try:
                dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            except Exception:
                dt = datetime.now(timezone.utc)
        else:
            dt = datetime.now(timezone.utc)

        # 3. Deduplication Check
        seq_num = packet.get("sequence_number")
        dedup_key = f"{shipment.id}:{seq_num}" if seq_num is not None else f"{shipment.id}:{dt.isoformat()}"
        
        if dedup_key in self._seen_packets:
            return {
                "status": "deduplicated",
                "message": "Duplicate packet received and safely ignored.",
                "dedup_key": dedup_key,
                "timestamp": dt.isoformat()
            }
        
        self._seen_packets[dedup_key] = datetime.now(timezone.utc)
        if len(self._seen_packets) > 5000:
            self._cleanup_old_cache()

        # 4. Extract Telemetry Fields
        p1 = float(packet.get("probe_1_temperature", packet.get("probe_1_temp", packet.get("temperature", 4.0))))
        p2 = packet.get("probe_2_temperature", packet.get("probe_2_temp"))
        p2 = float(p2) if p2 is not None else None
        
        ambient = float(packet.get("ambient_temperature", packet.get("ambient_temp", 28.0)))
        humidity = float(packet.get("humidity", 65.0))
        lat = float(packet.get("latitude", packet.get("lat", 12.9675)))
        lon = float(packet.get("longitude", packet.get("lon", 79.9427)))
        speed = float(packet.get("speed", 45.0))
        door_state = str(packet.get("door_state", "CLOSED")).upper()
        refrigeration_state = str(packet.get("refrigeration_state", "OPTIMAL")).upper()
        battery = float(packet.get("battery_level", packet.get("battery", 90.0)))
        signal_dbm = int(packet.get("signal_strength_dbm", packet.get("signal_dbm", -65)))
        sensor_code = packet.get("sensor_code", packet.get("sensor_id", shipment.sensor_id or "SN-IOT-001"))

        # 5. Fetch Previous Reading for Delta & Anomaly Analysis
        prev_reading = db.query(TelemetryReading).filter(
            TelemetryReading.shipment_id == shipment.id
        ).order_by(TelemetryReading.timestamp.desc()).first()

        # 6. Run Multi-Sensor Fault & Drift Diagnostics
        eff_temp, discrepancy, faults, is_valid = self.validate_sensor_health(
            sensor_id=sensor_code,
            probe_1=p1,
            probe_2=p2,
            ambient_temp=ambient,
            battery_level=battery,
            signal_dbm=signal_dbm,
            prev_reading=prev_reading
        )

        # 7. Persist Telemetry Record
        reading_id = f"tel_{uuid.uuid4().hex[:12]}"
        reading = TelemetryReading(
            id=reading_id,
            shipment_id=shipment.id,
            timestamp=dt,
            temperature=eff_temp,
            probe_1_temperature=p1,
            probe_2_temperature=p2,
            probe_discrepancy=discrepancy,
            sequence_number=seq_num,
            humidity=humidity,
            latitude=lat,
            longitude=lon,
            speed=speed,
            door_state=door_state,
            ambient_temperature=ambient,
            refrigeration_state=refrigeration_state,
            battery_level=battery,
            signal_strength_dbm=signal_dbm,
            sensor_fault_flags=faults,
            is_valid=is_valid
        )
        db.add(reading)

        # 8. Update Shipment Kinetic State (Arrhenius MKT & Current Temp)
        # Fetch last 20 readings for rate-of-change and kinetic integral
        recent_readings = db.query(TelemetryReading).filter(
            TelemetryReading.shipment_id == shipment.id,
            TelemetryReading.is_valid == True
        ).order_by(TelemetryReading.timestamp.desc()).limit(20).all()

        temps_series = [r.temperature for r in reversed(recent_readings)] + [eff_temp]
        current_mkt = calculate_mkt(temps_series) if len(temps_series) > 1 else eff_temp

        # Temperature rate of change (°C/min)
        if prev_reading and prev_reading.timestamp:
            time_delta_mins = max(0.1, (dt - prev_reading.timestamp).total_seconds() / 60.0)
            roc = (eff_temp - prev_reading.temperature) / time_delta_mins
            roc_status = "CRITICAL" if roc > 0.8 else ("WARNING" if roc > 0.3 else "NORMAL")
        else:
            roc_status = "NORMAL"

        shipment.current_temperature = eff_temp
        shipment.current_mkt = current_mkt
        shipment.updated_at = datetime.now(timezone.utc)

        # 9. Update Vehicle Location & Sensor Heartbeat
        if shipment.vehicle_id:
            veh = db.query(Vehicle).filter(Vehicle.id == shipment.vehicle_id).first()
            if veh:
                veh.current_latitude = lat
                veh.current_longitude = lon
                veh.refrigeration_status = refrigeration_state

        if shipment.sensor_id:
            sen = db.query(Sensor).filter(Sensor.id == shipment.sensor_id).first()
            if sen:
                sen.battery_level = battery
                sen.signal_strength_dbm = signal_dbm
                sen.last_seen_at = dt

        # 10. Run 4-Tier Hybrid Decision Engine
        extra_ctx = {
            "probe_1_temp": p1,
            "probe_2_temp": p2 if p2 is not None else p1,
            "probe_discrepancy": discrepancy,
            "humidity": humidity,
            "temp_min": shipment.temperature_min or 2.0,
            "hours_in_transit": 12.0
        }

        eval_result = evaluate_signals(
            current_temp=eff_temp,
            mkt=current_mkt,
            mkt_limit=shipment.mkt_limit or 8.0,
            temp_max=shipment.temperature_max or 8.0,
            roc_status=roc_status,
            door_state=door_state,
            speed=speed,
            ambient_temp=ambient,
            refrigeration_state=refrigeration_state,
            transit_delay_active=False,
            extra_context=extra_ctx
        )

        created_problem = None
        # Handle problem creation or escalation
        if eval_result["has_problem"]:
            active_prob = None
            if shipment.current_problem_id:
                active_prob = db.query(Problem).filter(
                    Problem.id == shipment.current_problem_id,
                    Problem.status.in_(["OPEN", "ACKNOWLEDGED", "ACTION_REQUIRED", "INVESTIGATING", "IN_PROGRESS"])
                ).first()
            if not active_prob:
                active_prob = db.query(Problem).filter(
                    Problem.shipment_id == shipment.id,
                    Problem.status.in_(["OPEN", "ACKNOWLEDGED", "ACTION_REQUIRED", "INVESTIGATING", "IN_PROGRESS"])
                ).order_by(Problem.detected_at.desc()).first()
                if active_prob:
                    shipment.current_problem_id = active_prob.id

            if not active_prob:
                raw_pt = eval_result["problem_type"]
                canon_pt = "TEMPERATURE_EXCURSION" if "temperature" in raw_pt.lower() else (
                    "REFRIGERATION_FAILURE" if "refrigeration" in raw_pt.lower() else (
                        "DOOR_AJAR" if "door" in raw_pt.lower() else raw_pt.upper()
                    )
                )
                prob_code = f"PR-{shipment.shipment_code.split('-')[-1] if '-' in shipment.shipment_code else '1001'}"
                new_prob = Problem(
                    id=f"prob_{uuid.uuid4().hex[:8]}",
                    problem_code=prob_code,
                    shipment_id=shipment.id,
                    problem_type=canon_pt,
                    severity=eval_result["severity"],
                    status="OPEN",
                    detected_at=dt,
                    evidence=eval_result["evidence"]
                )
                db.add(new_prob)
                shipment.current_problem_id = new_prob.id
                db.flush()

                # Generate Optimal Reroute via Spatial Routing Engine
                optimal_depot = spatial_routing_engine.find_optimal_depot(
                    db=db,
                    lat=lat,
                    lon=lon,
                    current_temp=eff_temp,
                    temp_ceiling=shipment.temperature_max or 8.0,
                    temp_floor=shipment.temperature_min or 2.0,
                    corridor=veh.corridor if shipment.vehicle_id and veh else "NH-48"
                )

                if optimal_depot:
                    rec = Recommendation(
                        id=f"rec_{uuid.uuid4().hex[:8]}",
                        problem_id=new_prob.id,
                        rec_type="REROUTE",
                        priority="CRITICAL" if eval_result["severity"] == "CRITICAL" else "HIGH",
                        description=f"Divert immediately to {optimal_depot['depot_name']} ({optimal_depot['road_distance_km']} km · {optimal_depot['eta_minutes']} min ETA)",
                        rationale=f"Kinetic feasibility: {optimal_depot['thermal_feasibility']['badge']}. Facility verified with {', '.join(optimal_depot['services'])}.",
                        target_depot_id=optimal_depot["depot_id"],
                        status="GENERATED"
                    )
                    db.add(rec)

                # Append to immutable audit chain
                append_audit_event(
                    db=db,
                    event_type="PROBLEM_DETECTED",
                    entity_type="SHIPMENT",
                    entity_id=shipment.id,
                    actor="IOT_INGESTION_ENGINE",
                    payload={
                        "severity": new_prob.severity,
                        "type": new_prob.problem_type,
                        "lat": lat,
                        "lon": lon,
                        "temp": eff_temp,
                        "mkt": current_mkt,
                        "sensor_faults": faults
                    }
                )
                created_problem = {
                    "id": new_prob.id,
                    "code": new_prob.problem_code,
                    "severity": new_prob.severity,
                    "type": new_prob.problem_type
                }

        db.commit()

        return {
            "status": "success",
            "reading_id": reading_id,
            "shipment_code": shipment.shipment_code,
            "effective_temperature": eff_temp,
            "probe_discrepancy": discrepancy,
            "current_mkt": round(current_mkt, 2),
            "sensor_fault_count": len(faults),
            "sensor_faults": faults,
            "decision": eval_result,
            "created_problem": created_problem
        }

    def ingest_batch(self, db: Session, packets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Reconciles and ingests an out-of-order burst of telemetry packets.
        Sorts chronologically, deduplicates, and updates states deterministically.
        """
        if not packets:
            return {"status": "empty", "ingested_count": 0, "results": []}

        # Helper to parse timestamp for sorting
        def parse_ts(p):
            t = p.get("timestamp")
            if isinstance(t, (int, float)):
                return t
            if isinstance(t, str):
                try:
                    return datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()
                except Exception:
                    pass
            return 0.0

        # Sort packets chronologically to resolve out-of-order jitter arrivals
        sorted_packets = sorted(packets, key=parse_ts)
        results = []
        dedup_count = 0
        success_count = 0

        for pkt in sorted_packets:
            res = self.ingest_packet(db, pkt)
            if res.get("status") == "deduplicated":
                dedup_count += 1
            elif res.get("status") == "success":
                success_count += 1
            results.append(res)

        return {
            "status": "batch_complete",
            "total_received": len(packets),
            "successfully_ingested": success_count,
            "deduplicated_count": dedup_count,
            "results": results
        }

iot_gateway = IoTTelemetryGateway()
