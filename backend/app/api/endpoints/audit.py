from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all import AuditEvent
from app.services.audit.audit_chain import AuditChain

router = APIRouter()

@router.get("/")
def get_audit_history(db: Session = Depends(get_db)):
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc()).all()
    return events

@router.post("/verify")
def verify_audit_chain(db: Session = Depends(get_db)):
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.asc()).all()
    result = AuditChain.verify_chain(events)
    return result
