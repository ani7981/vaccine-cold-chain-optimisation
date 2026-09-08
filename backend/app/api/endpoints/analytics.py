from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all import Shipment, Problem, Vehicle

router = APIRouter()

@router.get("/metrics")
def get_global_metrics(db: Session = Depends(get_db)):
    active_shipments = db.query(Shipment).filter(Shipment.status == "ACTIVE").count()
    total_problems = db.query(Problem).filter(Problem.status == "OPEN").count()
    critical_problems = db.query(Problem).filter(Problem.status == "OPEN", Problem.severity == "CRITICAL").count()
    total_vehicles = db.query(Vehicle).count()
    utilization_pct = round((active_shipments / total_vehicles * 100.0), 1) if total_vehicles > 0 else 0.0
    
    return {
        "active_shipments": active_shipments,
        "total_problems_open": total_problems,
        "critical_problems_open": critical_problems,
        "fleet_utilization": f"{utilization_pct}%",
        "total_vehicles": total_vehicles
    }
