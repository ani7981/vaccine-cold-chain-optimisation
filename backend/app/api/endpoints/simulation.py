from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.simulation.engine import simulation_engine

router = APIRouter()

@router.post("/start")
async def start_simulation(db: Session = Depends(get_db)):
    simulation_engine.start(db)
    return {"status": "started"}

@router.post("/stop")
async def stop_simulation(db: Session = Depends(get_db)):
    simulation_engine.stop(db)
    return {"status": "stopped"}

@router.post("/reset")
def reset_simulation(db: Session = Depends(get_db)):
    simulation_engine.stop(db)
    from seed import seed_db
    seed_db()
    return {"status": "reset_completed", "message": "Simulation halted and operational dataset restored to initial seed state"}
