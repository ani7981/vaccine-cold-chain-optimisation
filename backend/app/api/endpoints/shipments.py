from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all import Shipment, TelemetryReading, Problem, Location

router = APIRouter()

@router.get("/")
def list_shipments(db: Session = Depends(get_db)):
    shipments = db.query(Shipment).all()
    # Simple dictionary conversion for now
    return [{"id": s.id, "shipment_code": s.shipment_code, "status": s.status, "current_temperature": s.current_temperature} for s in shipments]

@router.get("/{shipment_id}")
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return {
        "id": shipment.id,
        "shipment_code": shipment.shipment_code,
        "status": shipment.status,
        "current_temperature": shipment.current_temperature,
        "current_mkt": shipment.current_mkt,
        "temperature_min": shipment.temperature_min,
        "temperature_max": shipment.temperature_max,
        "mkt_limit": shipment.mkt_limit
    }

@router.get("/{shipment_id}/telemetry")
def get_shipment_telemetry(shipment_id: str, db: Session = Depends(get_db)):
    readings = db.query(TelemetryReading).filter(TelemetryReading.shipment_id == shipment_id).order_by(TelemetryReading.timestamp.asc()).all()
    return [{"timestamp": r.timestamp, "temperature": r.temperature, "lat": r.latitude, "lon": r.longitude} for r in readings]

@router.get("/{shipment_id}/problems")
def get_shipment_problems(shipment_id: str, db: Session = Depends(get_db)):
    problems = db.query(Problem).filter(Problem.shipment_id == shipment_id).all()
    return [{"id": p.id, "problem_code": p.problem_code, "severity": p.severity, "status": p.status, "detected_at": p.detected_at, "evidence": p.evidence} for p in problems]

@router.get("/{shipment_id}/recommendations")
def get_shipment_recommendations(shipment_id: str, db: Session = Depends(get_db)):
    # Get all problems for shipment, then get recommendations for those problems
    problems = db.query(Problem.id).filter(Problem.shipment_id == shipment_id).subquery()
    from app.models.all import Recommendation
    recs = db.query(Recommendation).filter(Recommendation.problem_id.in_(problems)).all()
    return [{"id": r.id, "rec_type": r.rec_type, "priority": r.priority, "description": r.description, "rationale": r.rationale, "target_depot_id": r.target_depot_id, "status": r.status, "created_at": r.created_at} for r in recs]

