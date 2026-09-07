from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all import Problem, Shipment, Recommendation
from app.schemas import OperationalActionRequest
from app.services.audit.audit_chain import append_audit_event

router = APIRouter()


def serialize_problem(problem: Problem, db: Session):
    shipment = db.query(Shipment).filter(Shipment.id == problem.shipment_id).first()
    rec = db.query(Recommendation).filter(Recommendation.problem_id == problem.id).order_by(Recommendation.created_at.desc()).first()
    return {
        "id": problem.id, "problem_code": problem.problem_code, "shipment_id": problem.shipment_id,
        "shipment_code": shipment.shipment_code if shipment else None,
        "problem_type": problem.problem_type, "severity": problem.severity, "status": problem.status,
        "detected_at": problem.detected_at, "resolved_at": problem.resolved_at,
        "evidence": problem.evidence or {}, "rule_results": problem.rule_results or {},
        "recommendation": ({"id": rec.id, "rec_type": rec.rec_type, "description": rec.description,
                            "rationale": rec.rationale, "status": rec.status,
                            "target_depot_id": rec.target_depot_id} if rec else None),
    }


@router.get("/")
def list_problems(db: Session = Depends(get_db)):
    return [serialize_problem(p, db) for p in db.query(Problem).order_by(Problem.detected_at.desc()).all()]


@router.get("/{problem_id}")
def get_problem(problem_id: str, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter((Problem.id == problem_id) | (Problem.problem_code == problem_id)).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return serialize_problem(problem, db)


@router.post("/{problem_id}/acknowledge")
def acknowledge_problem(problem_id: str, body: OperationalActionRequest, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.status == "OPEN":
        problem.status = "ACKNOWLEDGED"
        append_audit_event(db, "PROBLEM_ACKNOWLEDGED", "PROBLEM", problem.id, "DEMO_OPERATOR", {"note": body.note or ""})
        db.commit()
    return serialize_problem(problem, db)


@router.post("/{problem_id}/override")
def override_problem(problem_id: str, body: OperationalActionRequest, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.status not in {"REROUTED", "OVERRIDDEN", "RESOLVED"}:
        problem.status = "OVERRIDDEN"
        problem.resolved_at = datetime.now(timezone.utc)
        shipment = db.query(Shipment).filter(Shipment.id == problem.shipment_id).first()
        if shipment:
            shipment.current_problem_id = None
        append_audit_event(db, "PROBLEM_OVERRIDDEN", "PROBLEM", problem.id, "DEMO_OPERATOR", {"note": body.note or ""})
        db.commit()
    return serialize_problem(problem, db)
