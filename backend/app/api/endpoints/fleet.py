from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all import Shipment, Vehicle, Problem

router = APIRouter()

@router.get("/")
def get_fleet_status(db: Session = Depends(get_db)):
    shipments = db.query(Shipment).all()
    vehicles = db.query(Vehicle).all()
    problems = db.query(Problem).filter(Problem.status == "OPEN").all()
    
    total = len(shipments)
    healthy = sum(1 for s in shipments if s.status == "ACTIVE" and s.current_problem_id is None)
    attention = sum(1 for s in shipments if s.status == "ACTIVE" and s.current_problem_id is not None)
    delayed = 0  # To be calculated if estimated_arrival > now
    
    return {
        "total_shipments": total,
        "healthy": healthy,
        "attention": attention,
        "problems": len(problems),
        "temperature_issues": sum(1 for p in problems if p.problem_type == "temperature_problem"),
        "delayed_shipments": delayed,
        "active_vehicles": len(vehicles)
    }
