from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all import Shipment, Problem, Vehicle, TelemetryReading
from app.services.ai import ai_service

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

@router.get("/ai-model-info")
def get_ai_model_info():
    """Return trained AI model architectures, training dataset, and validation metrics."""
    return {
        "status": "ready" if ai_service.is_ready() else "initializing",
        "metadata": ai_service.metadata
    }

@router.get("/ai-insights/{shipment_id}")
def get_shipment_ai_insights(shipment_id: str, db: Session = Depends(get_db)):
    """Run real-time XGBoost spoilage risk and temperature forecasting on active shipment."""
    shipment = db.query(Shipment).filter(
        (Shipment.id == shipment_id) | (Shipment.shipment_code == shipment_id)
    ).first()
    
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    latest_readings = db.query(TelemetryReading).filter(
        TelemetryReading.shipment_id == shipment.id
    ).order_by(TelemetryReading.timestamp.desc()).limit(10).all()
    
    temp = shipment.current_temperature if shipment.current_temperature is not None else 4.0
    ambient = 32.0
    humidity = 65.0
    delta_1h = 0.0
    
    if latest_readings:
        first = latest_readings[0]
        ambient = first.ambient_temperature if first.ambient_temperature is not None else 32.0
        humidity = first.humidity if first.humidity is not None else 65.0
        if len(latest_readings) > 1 and latest_readings[0].timestamp and latest_readings[-1].timestamp:
            temps_win = [r.temperature for r in latest_readings]
            temp_range = max(temps_win) - min(temps_win)
            if temp_range <= 0.35 and 2.0 <= temp <= 6.5:
                # Normal thermostat cycling around setpoint - rate of change is effectively zero
                delta_1h = 0.0
            else:
                dt_mins = max(0.1, abs((latest_readings[0].timestamp - latest_readings[-1].timestamp).total_seconds()) / 60.0)
                if dt_mins >= 0.5:
                    rate_per_hour = (latest_readings[0].temperature - latest_readings[-1].temperature) / (dt_mins / 60.0)
                    # Physical constraint for insulated containers: max passive rise is ~1.8°C/h, active pulldown ~-2.5°C/h
                    delta_1h = max(-2.5, min(1.8, round(rate_per_hour, 2)))
                else:
                    delta_1h = max(-2.5, min(1.8, round(first.temperature - latest_readings[1].temperature, 2)))

    # Check active problem evidence for confirmed thermal trajectory
    if shipment.current_problem_id:
        prob = db.query(Problem).filter(Problem.id == shipment.current_problem_id).first()
        if prob and prob.status in ["OPEN", "IN_PROGRESS", "ACTION_REQUIRED", "ACKNOWLEDGED", "INVESTIGATING"]:
            ev = prob.evidence or {}
            if "rate_of_rise" in ev and delta_1h <= 0.0:
                try:
                    ror_val = str(ev["rate_of_rise"]).replace("°C/min", "").replace("°C/h", "").replace("+", "").strip()
                    delta_1h = max(0.1, min(1.8, round(float(ror_val), 2)))
                except Exception:
                    pass

    # Calculate cumulative OOB hours
    oob_count = sum(1 for r in latest_readings if r.temperature > shipment.temperature_max or r.temperature < shipment.temperature_min)
    oob_hours = round(oob_count * 0.25, 2)
    
    raw_feats = {
        "temperature": temp,
        "ambient_temperature": ambient,
        "humidity": humidity,
        "temp_delta_1h": delta_1h,
        "out_of_bound_temperature_hours": oob_hours,
        "item_expiry_hours": 720.0,
        "refrigeration_temperature_hours": 14.0
    }
    
    prediction = ai_service.predict(raw_feats, temp_ceiling=shipment.temperature_max)
    
    return {
        "shipment_code": shipment.shipment_code,
        "current_temperature": temp,
        "temperature_ceiling": shipment.temperature_max,
        "temperature_floor": shipment.temperature_min,
        "mkt": shipment.current_mkt,
        "prediction": prediction
    }

class AISimulateRequest(BaseModel):
    temperature: float = Field(default=4.0, description="Chamber temperature in Celsius")
    ambient_temperature: float = Field(default=32.0, description="Ambient exterior temperature in Celsius")
    humidity: float = Field(default=65.0, description="Relative humidity %")
    temp_delta_1h: float = Field(default=0.0, description="1-hour rate of change in °C/h")
    probe_discrepancy: float = Field(default=0.05, description="Probe discrepancy in °C")
    temperature_ceiling: float = Field(default=8.0, description="Upper threshold in °C")

@router.post("/ai-simulate")
def simulate_custom_ai_inference(req: AISimulateRequest):
    """Run real-time XGBoost inference on custom counterfactual / what-if inputs."""
    raw_feats = {
        "temperature": req.temperature,
        "ambient_temperature": req.ambient_temperature,
        "humidity": req.humidity,
        "temp_delta_1h": req.temp_delta_1h,
        "probe_discrepancy": req.probe_discrepancy,
        "out_of_bound_temperature_hours": max(0.0, req.temperature - req.temperature_ceiling) * 0.5 if req.temperature > req.temperature_ceiling else 0.0,
        "item_expiry_hours": 720.0,
        "refrigeration_temperature_hours": 14.0
    }
    prediction = ai_service.predict(raw_feats, temp_ceiling=req.temperature_ceiling)
    return {
        "inputs": req.dict(),
        "prediction": prediction
    }


