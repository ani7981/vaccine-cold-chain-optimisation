import asyncio
import random
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.all import Simulation, Shipment, TelemetryReading, TransitEvent, Vehicle
from app.services.detection.mkt import calculate_mkt
from app.services.detection.correlation import evaluate_signals
from app.services.detection.rate_of_change import RateOfChangeDetector
from app.services.audit.audit_chain import AuditChain
from app.websocket.manager import manager
from app.core.database import SessionLocal

class SimulationEngine:
    def __init__(self):
        self.is_running = False
        self.task = None
        self.roc_detector = RateOfChangeDetector(warning_threshold=0.1, critical_threshold=0.2, sustained_duration_seconds=300)

    def start(self, db: Session, scenario: str = "chennai_vellore"):
        sim = db.query(Simulation).first()
        if not sim:
            sim = Simulation(scenario=scenario, status="RUNNING")
            db.add(sim)
        else:
            sim.status = "RUNNING"
            sim.scenario = scenario
            sim.current_tick = 0
            
        db.commit()
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_loop(scenario))
        
    def stop(self, db: Session):
        self.is_running = False
        if self.task:
            self.task.cancel()
        sim = db.query(Simulation).first()
        if sim:
            sim.status = "STOPPED"
            db.commit()
            
    async def _run_loop(self, scenario: str):
        # We simulate a tick every 2 seconds real time, which might be 5 minutes sim time
        # For simplicity, we just create a hardcoded route for VK-1042
        
        # Hardcoded route coordinates from Chennai to Vellore approx
        route = [
            (13.0827, 80.2707), # Chennai
            (13.0232, 80.0558),
            (12.9716, 79.9406), # Sriperumbudur
            (12.9242, 79.8035),
            (12.8943, 79.7214), # Kanchipuram
            (12.9202, 79.1325), # Vellore
        ]
        
        tick = 0
        while self.is_running:
            db = SessionLocal()
            try:
                sim = db.query(Simulation).first()
                if not sim or sim.status != "RUNNING":
                    break
                    
                shipment = db.query(Shipment).filter(Shipment.shipment_code == "VK-1042").first()
                if not shipment:
                    continue

                vehicle = db.query(Vehicle).filter(Vehicle.id == shipment.vehicle_id).first()
                
                # Progression logic
                progress = tick / 100.0
                if progress >= 1.0:
                    self.is_running = False
                    sim.status = "COMPLETED"
                    db.commit()
                    break
                
                # Interpolate coordinate
                idx = int(progress * (len(route) - 1))
                lat, lon = route[idx]
                
                # Temperature logic (deterministic degradation)
                # Normal 2.0 - 4.0
                base_temp = 3.0
                door_state = "CLOSED"
                refrigeration_state = "NORMAL"
                ambient_temp = 35.0
                speed = 60.0
                transit_delay = False
                
                if tick > 30 and tick < 60:
                    # Degradation phase
                    base_temp = 3.0 + (tick - 30) * 0.15 # goes up to 7.5
                    if tick > 40:
                        refrigeration_state = "DEGRADED"
                elif tick >= 60:
                    # Recovery phase
                    base_temp = 7.5 - (tick - 60) * 0.1
                    if base_temp < 3.0:
                        base_temp = 3.0
                        
                # Add some jitter
                temp = base_temp + random.uniform(-0.1, 0.1)
                
                # Save reading
                reading = TelemetryReading(
                    id=f"reading_{tick}",
                    shipment_id=shipment.id,
                    timestamp=datetime.now(timezone.utc),
                    temperature=temp,
                    humidity=45.0,
                    latitude=lat,
                    longitude=lon,
                    speed=speed,
                    door_state=door_state,
                    ambient_temperature=ambient_temp,
                    refrigeration_state=refrigeration_state
                )
                db.add(reading)
                db.flush()
                
                # Update shipment current state
                shipment.current_temperature = temp
                
                # Get last N readings for MKT and ROC
                recent_readings = db.query(TelemetryReading).filter(
                    TelemetryReading.shipment_id == shipment.id
                ).order_by(TelemetryReading.timestamp.desc()).limit(20).all()
                
                readings_dict = [{"timestamp": r.timestamp, "temperature": r.temperature} for r in recent_readings]
                
                roc_status = self.roc_detector.check(readings_dict)
                mkt = calculate_mkt([r["temperature"] for r in readings_dict])
                shipment.current_mkt = mkt
                
                # Evaluate signals
                eval_result = evaluate_signals(
                    current_temp=temp,
                    mkt=mkt,
                    mkt_limit=shipment.mkt_limit,
                    temp_max=shipment.temperature_max,
                    roc_status=roc_status,
                    door_state=door_state,
                    speed=speed,
                    ambient_temp=ambient_temp,
                    refrigeration_state=refrigeration_state,
                    transit_delay_active=transit_delay
                )
                
                sim.current_tick = tick
                
                # Check for new problem
                if eval_result["has_problem"] and eval_result["severity"] in ["HIGH", "CRITICAL"]:
                    # Is there already an open problem of this type for this shipment?
                    from app.models.all import Problem, Recommendation, AuditEvent
                    existing_prob = db.query(Problem).filter(
                        Problem.shipment_id == shipment.id,
                        Problem.status == "OPEN",
                        Problem.problem_type == eval_result["problem_type"]
                    ).first()
                    
                    if not existing_prob:
                        new_prob = Problem(
                            id=f"prob_{tick}_{shipment.id}",
                            problem_code=f"PRB-{eval_result['problem_type'].upper()}-{tick}",
                            shipment_id=shipment.id,
                            problem_type=eval_result["problem_type"],
                            severity=eval_result["severity"],
                            status="OPEN",
                            detected_at=datetime.now(timezone.utc),
                            evidence=eval_result["evidence"]
                        )
                        db.add(new_prob)
                        shipment.current_problem_id = new_prob.id
                        db.flush()
                        
                        # Generate recommendation via PostGIS nearest depot
                        from app.services.routing.nearest_depot import find_nearest_depot
                        nearest_depot = find_nearest_depot(db, lat, lon)
                        
                        if nearest_depot:
                            rec = Recommendation(
                                id=f"rec_{tick}_{new_prob.id}",
                                problem_id=new_prob.id,
                                rec_type="REROUTE",
                                priority="CRITICAL",
                                description=f"Reroute immediately to {nearest_depot.name}",
                                rationale="Nearest suitable refrigeration facility capable of cross-docking.",
                                target_depot_id=nearest_depot.id,
                                status="GENERATED"
                            )
                            db.add(rec)
                            
                        # Audit Trail
                        last_audit = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).first()
                        prev_hash = last_audit.hash if last_audit else AuditChain.GENESIS_HASH
                        
                        audit_payload = {
                            "severity": new_prob.severity,
                            "type": new_prob.problem_type,
                            "lat": lat,
                            "lon": lon,
                            "temp": temp
                        }
                        new_hash = AuditChain.compute_hash(prev_hash, new_prob.detected_at, "PROBLEM_DETECTED", "SHIPMENT", shipment.id, audit_payload)
                        
                        audit_event = AuditEvent(
                            id=f"audit_{tick}",
                            timestamp=new_prob.detected_at,
                            event_type="PROBLEM_DETECTED",
                            entity_type="SHIPMENT",
                            entity_id=shipment.id,
                            actor="SYSTEM_DETECTION_ENGINE",
                            payload=audit_payload,
                            previous_hash=prev_hash,
                            hash=new_hash
                        )
                        db.add(audit_event)
                
                db.commit()
                
                # Broadcast
                await manager.broadcast({
                    "type": "TELEMETRY_UPDATE",
                    "payload": {
                        "shipment_code": shipment.shipment_code,
                        "temperature": temp,
                        "mkt": mkt,
                        "lat": lat,
                        "lon": lon,
                        "speed": speed,
                        "roc_status": roc_status,
                        "problem_status": eval_result,
                        "tick": tick
                    }
                })
                
                tick += 1
            except Exception as e:
                print(f"Simulation error: {e}")
            finally:
                db.close()
                
            await asyncio.sleep(2.0) # 2 seconds real time per tick

simulation_engine = SimulationEngine()
