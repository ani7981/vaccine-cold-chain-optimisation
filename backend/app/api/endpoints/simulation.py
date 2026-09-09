from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.simulation.engine import simulation_engine
from app.services.simulation.chaos import chaos_manager

router = APIRouter()

class StartSimulationRequest(BaseModel):
    scenario: str = "pan_india_dynamic"

class ChaosIncidentRequest(BaseModel):
    shipment_id: str = Field(default="ship_1", description="Target consignment ID")
    incident_type: str = Field(
        default="COMPRESSOR_FAILURE",
        description="One of: COMPRESSOR_FAILURE, HEATWAVE_SURGE, DOOR_AJAR, TRAFFIC_GRIDLOCK, SENSOR_PROBE_DRIFT, NORMAL"
    )
    duration_seconds: int = Field(default=300, description="Duration in seconds before auto-recovering (default 300s)")

@router.post("/start")
async def start_simulation(req: Optional[StartSimulationRequest] = None, db: Session = Depends(get_db)):
    scenario = req.scenario if req else "pan_india_dynamic"
    simulation_engine.start(db, scenario=scenario)
    return {
        "status": "started",
        "scenario": scenario,
        "engine_architecture": "Newton-Fourier Thermal Conduction + Diurnal Solar Microclimates + Multi-Convoy IoT Ingestion"
    }

@router.post("/stop")
async def stop_simulation(db: Session = Depends(get_db)):
    simulation_engine.stop(db)
    return {"status": "stopped"}

@router.post("/reset")
def reset_simulation(db: Session = Depends(get_db)):
    simulation_engine.stop(db)
    db.close()
    from seed import seed_db
    seed_db()
    return {"status": "reset_completed", "message": "Simulation halted and operational dataset restored to initial seed state"}

@router.get("/status")
def get_simulation_status():
    return simulation_engine.get_status()

@router.post("/inject-incident")
def inject_simulation_incident(req: ChaosIncidentRequest):
    try:
        res = simulation_engine.inject_chaos(
            shipment_id=req.shipment_id,
            incident_type=req.incident_type,
            duration_seconds=req.duration_seconds
        )
        return res
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))

@router.post("/clear-incidents")
def clear_simulation_incidents(shipment_id: Optional[str] = None):
    simulation_engine.clear_chaos(shipment_id=shipment_id)
    return {"status": "cleared", "target": shipment_id or "all_shipments"}
