from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.all import Problem, Shipment, Recommendation, AuditEvent
from app.schemas import OperationalActionRequest, IncidentResolutionRequest, IncidentTransitionRequest
from app.services.audit.audit_chain import append_audit_event
from app.websocket.manager import manager

router = APIRouter()


def serialize_problem(problem: Problem, db: Session):
    shipment = db.query(Shipment).filter(Shipment.id == problem.shipment_id).first()
    rec = db.query(Recommendation).filter(Recommendation.problem_id == problem.id).order_by(Recommendation.created_at.desc()).first()
    return {
        "id": problem.id,
        "problem_code": problem.problem_code,
        "shipment_id": problem.shipment_id,
        "shipment_code": shipment.shipment_code if shipment else None,
        "problem_type": problem.problem_type,
        "severity": problem.severity,
        "status": problem.status,
        "detected_at": problem.detected_at.isoformat() if problem.detected_at else None,
        "resolved_at": problem.resolved_at.isoformat() if problem.resolved_at else None,
        "resolution_reason": problem.resolution_reason,
        "corrective_action": problem.corrective_action,
        "resolution_notes": problem.resolution_notes,
        "resolved_by_user": problem.resolved_by_user,
        "evidence": problem.evidence or {},
        "rule_results": problem.rule_results or {},
        "recommendation": ({
            "id": rec.id,
            "rec_type": rec.rec_type,
            "description": rec.description,
            "rationale": rec.rationale,
            "status": rec.status,
            "target_depot_id": rec.target_depot_id
        } if rec else None),
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


@router.get("/{problem_id}/history")
def get_problem_history(problem_id: str, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter((Problem.id == problem_id) | (Problem.problem_code == problem_id)).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    events = db.query(AuditEvent).filter(AuditEvent.entity_id == problem.id).order_by(AuditEvent.timestamp.asc()).all()
    return [{
        "id": e.id, "timestamp": e.timestamp, "event_type": e.event_type,
        "actor": e.actor, "payload": e.payload, "hash": e.hash
    } for e in events]


@router.post("/{problem_id}/acknowledge")
async def acknowledge_problem(problem_id: str, body: OperationalActionRequest, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter((Problem.id == problem_id) | (Problem.problem_code == problem_id)).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.status == "OPEN":
        problem.status = "ACKNOWLEDGED"
        append_audit_event(db, "PROBLEM_ACKNOWLEDGED", "PROBLEM", problem.id, "DEMO_OPERATOR", {"note": body.note or ""})
        db.commit()
    serialized = serialize_problem(problem, db)
    try:
        await manager.broadcast({
            "type": "incident.acknowledged",
            "problem_id": problem.id,
            "problem_code": problem.problem_code,
            "status": problem.status,
            "data": serialized
        })
    except Exception:
        pass
    return serialized


@router.post("/{problem_id}/transition")
async def transition_problem(problem_id: str, body: IncidentTransitionRequest, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter((Problem.id == problem_id) | (Problem.problem_code == problem_id)).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    valid_states = {"OPEN", "INVESTIGATING", "ACTION_REQUIRED", "RESOLVED"}
    target_status = body.status.upper()
    if target_status not in valid_states:
        raise HTTPException(status_code=400, detail=f"Invalid status {body.status}. Must be one of {list(valid_states)}")
    
    old_status = problem.status
    problem.status = target_status
    if target_status == "RESOLVED":
        problem.resolved_at = datetime.now(timezone.utc)
        problem.resolved_by_user = body.user or "OPERATOR_HQ"
        if body.notes:
            problem.resolution_notes = body.notes
        shipment = db.query(Shipment).filter(Shipment.id == problem.shipment_id).first()
        if shipment and shipment.current_problem_id == problem.id:
            shipment.current_problem_id = None
    
    append_audit_event(
        db,
        "INCIDENT_TRANSITIONED",
        "PROBLEM",
        problem.id,
        body.user or "OPERATOR_HQ",
        {
            "problem_code": problem.problem_code,
            "from_status": old_status,
            "to_status": target_status,
            "notes": body.notes or ""
        }
    )
    db.commit()

    serialized = serialize_problem(problem, db)
    try:
        await manager.broadcast({
            "type": "incident.transitioned",
            "problem_id": problem.id,
            "problem_code": problem.problem_code,
            "from_status": old_status,
            "to_status": target_status,
            "data": serialized
        })
    except Exception:
        pass
    return serialized


@router.post("/{problem_id}/resolve")
async def resolve_problem(problem_id: str, body: IncidentResolutionRequest, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter((Problem.id == problem_id) | (Problem.problem_code == problem_id)).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    problem.status = "RESOLVED"
    problem.resolved_at = datetime.now(timezone.utc)
    problem.resolution_reason = body.reason
    problem.corrective_action = body.corrective_action
    problem.resolution_notes = body.notes or ""
    problem.resolved_by_user = body.user or "OPERATOR_HQ"

    evidence = dict(problem.evidence or {})
    evidence["resolution"] = {
        "reason": body.reason,
        "corrective_action": body.corrective_action,
        "notes": body.notes or "",
        "resolved_by": body.user or "OPERATOR_HQ",
        "resolved_at": problem.resolved_at.isoformat()
    }
    problem.evidence = evidence

    shipment = db.query(Shipment).filter(Shipment.id == problem.shipment_id).first()
    if shipment and shipment.current_problem_id == problem.id:
        shipment.current_problem_id = None

    append_audit_event(
        db,
        "INCIDENT_RESOLVED",
        "PROBLEM",
        problem.id,
        body.user or "OPERATOR_HQ",
        {
            "problem_code": problem.problem_code,
            "reason": body.reason,
            "corrective_action": body.corrective_action,
            "notes": body.notes or "",
            "resolved_at": problem.resolved_at.isoformat()
        }
    )
    db.commit()

    serialized = serialize_problem(problem, db)
    try:
        await manager.broadcast({
            "type": "incident.resolved",
            "problem_id": problem.id,
            "problem_code": problem.problem_code,
            "status": "RESOLVED",
            "data": serialized
        })
    except Exception:
        pass
    # Telegram: notify supervisors of resolution
    try:
        from app.services.notifications.telegram import notify_incident_resolved
        import asyncio
        asyncio.create_task(notify_incident_resolved(serialized))
    except Exception:
        pass
    return serialized


@router.post("/{problem_id}/override")
async def override_problem(problem_id: str, body: OperationalActionRequest, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter((Problem.id == problem_id) | (Problem.problem_code == problem_id)).first()
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
    serialized = serialize_problem(problem, db)
    try:
        await manager.broadcast({
            "type": "incident.overridden",
            "problem_id": problem.id,
            "problem_code": problem.problem_code,
            "status": problem.status,
            "data": serialized
        })
    except Exception:
        pass
    return serialized
