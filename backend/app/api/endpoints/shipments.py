from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all import Shipment, TelemetryReading, Problem, Location, Vehicle, Sensor, Product, Recommendation, Depot, TransitEvent
from app.schemas import RerouteRequest
from app.services.audit.audit_chain import append_audit_event

router = APIRouter()


def _shipment(db: Session, value: str):
    return db.query(Shipment).filter((Shipment.id == value) | (Shipment.shipment_code == value)).first()


def serialize_shipment(s: Shipment, db: Session, detailed: bool = False):
    origin = db.query(Location).filter(Location.id == s.origin_location_id).first()
    destination = db.query(Location).filter(Location.id == s.destination_location_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == s.vehicle_id).first()
    sensor = db.query(Sensor).filter(Sensor.id == s.sensor_id).first()
    product = db.query(Product).filter(Product.id == s.product_id).first()
    latest = db.query(TelemetryReading).filter(TelemetryReading.shipment_id == s.id).order_by(TelemetryReading.timestamp.desc()).first()
    problem = db.query(Problem).filter(Problem.id == s.current_problem_id).first()
    data = {
        "id": s.id, "shipment_code": s.shipment_code, "status": s.status,
        "current_temperature": s.current_temperature, "current_mkt": s.current_mkt,
        "temperature_min": s.temperature_min, "temperature_max": s.temperature_max, "mkt_limit": s.mkt_limit,
        "started_at": s.started_at, "estimated_arrival": s.estimated_arrival,
        "origin": ({"id": origin.id, "name": origin.name, "city": origin.city, "lat": origin.latitude, "lon": origin.longitude} if origin else None),
        "destination": ({"id": destination.id, "name": destination.name, "city": destination.city, "lat": destination.latitude, "lon": destination.longitude} if destination else None),
        "vehicle": ({"id": vehicle.id, "code": vehicle.vehicle_code, "registration_number": vehicle.registration_number, "refrigeration_status": vehicle.refrigeration_status} if vehicle else None),
        "sensor": ({"id": sensor.id, "code": sensor.sensor_code, "calibration_status": sensor.calibration_status} if sensor else None),
        "latest_telemetry": ({"timestamp": latest.timestamp, "temperature": latest.temperature, "humidity": latest.humidity,
                              "lat": latest.latitude, "lon": latest.longitude, "speed": latest.speed, "door_state": latest.door_state,
                              "ambient_temperature": latest.ambient_temperature, "refrigeration_state": latest.refrigeration_state} if latest else None),
        "current_problem": ({"id": problem.id, "problem_code": problem.problem_code, "severity": problem.severity, "status": problem.status, "problem_type": problem.problem_type} if problem else None),
    }
    if detailed:
        data["product"] = ({"name": product.name, "activation_energy": product.activation_energy} if product else None)
    return data

@router.get("/")
def list_shipments(db: Session = Depends(get_db)):
    return [serialize_shipment(s, db) for s in db.query(Shipment).order_by(Shipment.shipment_code).all()]

@router.get("/{shipment_id}")
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    shipment = _shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return serialize_shipment(shipment, db, detailed=True)

@router.get("/{shipment_id}/telemetry")
def get_shipment_telemetry(shipment_id: str, db: Session = Depends(get_db)):
    shipment = _shipment(db, shipment_id)
    if not shipment: raise HTTPException(status_code=404, detail="Shipment not found")
    readings = db.query(TelemetryReading).filter(TelemetryReading.shipment_id == shipment.id).order_by(TelemetryReading.timestamp.asc()).all()
    return [{"timestamp": r.timestamp, "temperature": r.temperature, "humidity": r.humidity, "lat": r.latitude, "lon": r.longitude, "speed": r.speed, "door_state": r.door_state, "ambient_temperature": r.ambient_temperature, "refrigeration_state": r.refrigeration_state} for r in readings]

@router.get("/{shipment_id}/problems")
def get_shipment_problems(shipment_id: str, db: Session = Depends(get_db)):
    shipment = _shipment(db, shipment_id)
    if not shipment: raise HTTPException(status_code=404, detail="Shipment not found")
    problems = db.query(Problem).filter(Problem.shipment_id == shipment.id).all()
    return [{"id": p.id, "problem_code": p.problem_code, "severity": p.severity, "status": p.status, "detected_at": p.detected_at, "evidence": p.evidence} for p in problems]

@router.get("/{shipment_id}/recommendations")
def get_shipment_recommendations(shipment_id: str, db: Session = Depends(get_db)):
    # Get all problems for shipment, then get recommendations for those problems
    shipment = _shipment(db, shipment_id)
    if not shipment: raise HTTPException(status_code=404, detail="Shipment not found")
    problems = db.query(Problem.id).filter(Problem.shipment_id == shipment.id).subquery()
    from app.models.all import Recommendation
    recs = db.query(Recommendation).filter(Recommendation.problem_id.in_(problems)).all()
    return [{"id": r.id, "rec_type": r.rec_type, "priority": r.priority, "description": r.description, "rationale": r.rationale, "target_depot_id": r.target_depot_id, "status": r.status, "created_at": r.created_at} for r in recs]


@router.post("/{shipment_id}/reroute")
def authorize_reroute(shipment_id: str, body: RerouteRequest, db: Session = Depends(get_db)):
    shipment = _shipment(db, shipment_id)
    if not shipment: raise HTTPException(status_code=404, detail="Shipment not found")
    problem = db.query(Problem).filter(Problem.id == shipment.current_problem_id).first()
    if not problem: raise HTTPException(status_code=409, detail="No active problem has a reroute recommendation")
    recommendation = db.query(Recommendation).filter(Recommendation.problem_id == problem.id, Recommendation.rec_type == "REROUTE").order_by(Recommendation.created_at.desc()).first()
    target_id = body.target_depot_id or (recommendation.target_depot_id if recommendation else None)
    depot = db.query(Depot).filter(Depot.id == target_id).first() if target_id else None
    if not depot: raise HTTPException(status_code=409, detail="No eligible reroute depot is available")
    if recommendation:
        recommendation.status = "EXECUTED"
        recommendation.executed_at = datetime.now(timezone.utc)
    problem.status = "REROUTED"
    shipment.status = "REROUTED"
    event = TransitEvent(id=f"transit_{shipment.id}_{uuid.uuid4().hex[:8]}", shipment_id=shipment.id, timestamp=datetime.now(timezone.utc), event_type="REROUTE_AUTHORIZED", status="ACTIVE", duration=None, event_metadata={"target_depot_id": depot.id, "target_depot_name": depot.name})
    db.add(event)
    append_audit_event(db, "REROUTE_AUTHORIZED", "SHIPMENT", shipment.id, "DEMO_OPERATOR", {"problem_id": problem.id, "target_depot_id": depot.id, "target_depot_name": depot.name})
    db.commit()
    return {"shipment": serialize_shipment(shipment, db, detailed=True), "target_depot": {"id": depot.id, "name": depot.name, "lat": depot.latitude, "lon": depot.longitude}, "problem_id": problem.id}
