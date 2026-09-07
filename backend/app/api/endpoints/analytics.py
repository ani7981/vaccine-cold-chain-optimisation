from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all import Shipment, Problem

router = APIRouter()

@router.get("/metrics")
def get_global_metrics(db: Session = Depends(get_db)):
    active_shipments = db.query(Shipment).filter(Shipment.status == "ACTIVE").count()
    total_problems = db.query(Problem).filter(Problem.status == "OPEN").count()
    critical_problems = db.query(Problem).filter(Problem.status == "OPEN", Problem.severity == "CRITICAL").count()
    
    return {
        "active_shipments": active_shipments,
        "total_problems_open": total_problems,
        "critical_problems_open": critical_problems,
        "fleet_utilization": None
    }
