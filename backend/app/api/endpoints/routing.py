from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.core.database import get_db
from app.models.all import Shipment, Vehicle, Product, Problem
from app.services.routing.engine import spatial_routing_engine, CORRIDORS

router = APIRouter()

@router.get("/corridors")
def get_corridors():
    """Returns national cold-chain highway corridor geometries for GIS map layers."""
    return {
        "status": "success",
        "corridors": CORRIDORS
    }

@router.get("/reroute-candidates/{shipment_id}")
def get_reroute_candidates(
    shipment_id: str,
    db: Session = Depends(get_db)
):
    """
    Evaluates optimal cold-chain diversion facilities for an active shipment:
    1. Extracts live vehicle GPS coordinates & corridor.
    2. Gathers thermal telemetry & breach forecast.
    3. Runs 3-Tier PostGIS Geodetics + OSRM/Corridor Road Router + Thermal Feasibility Engine.
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    vehicle = db.query(Vehicle).filter(Vehicle.id == shipment.vehicle_id).first() if shipment.vehicle_id else None
    product = db.query(Product).filter(Product.id == shipment.product_id).first() if shipment.product_id else None
    problem = db.query(Problem).filter(Problem.id == shipment.current_problem_id).first() if shipment.current_problem_id else None

    # Current coordinates: vehicle GPS or default to shipment origin
    lat = vehicle.current_latitude if vehicle and vehicle.current_latitude else 12.9675
    lon = vehicle.current_longitude if vehicle and vehicle.current_longitude else 79.9427
    corridor = vehicle.corridor if vehicle else "NH-48"

    current_temp = float(shipment.current_temperature or 4.5)
    temp_ceiling = float(shipment.temperature_max or 8.0)
    temp_floor = float(shipment.temperature_min or 2.0)
    requires_deep_freeze = (product.temperature_min < -30.0) if product else False

    # Extract dynamic thermal velocity from problem evidence or defaults
    evidence = problem.evidence if problem and problem.evidence else {}
    roc_status = evidence.get("rate_of_change", "NORMAL")
    rate_of_change = 0.8 if roc_status == "CRITICAL" else (0.4 if roc_status == "WARNING" else 0.05)

    candidates = spatial_routing_engine.find_reroute_candidates(
        db=db,
        lat=lat,
        lon=lon,
        requires_deep_freeze=requires_deep_freeze,
        current_temp=current_temp,
        temp_ceiling=temp_ceiling,
        temp_floor=temp_floor,
        rate_of_change=rate_of_change,
        corridor=corridor,
        max_candidates=4
    )

    return {
        "shipment_id": shipment.id,
        "shipment_code": shipment.shipment_code,
        "vehicle": {
            "id": vehicle.id if vehicle else None,
            "code": vehicle.vehicle_code if vehicle else "UNKNOWN",
            "model": vehicle.model if vehicle else "Reefer Carrier",
            "driver_name": vehicle.driver_name if vehicle else "Driver on duty",
            "driver_phone": vehicle.driver_phone if vehicle else None,
            "corridor": corridor,
            "current_coordinates": [lat, lon]
        },
        "thermal_state": {
            "current_temperature": current_temp,
            "temp_ceiling": temp_ceiling,
            "temp_floor": temp_floor,
            "rate_of_change": rate_of_change,
            "requires_deep_freeze": requires_deep_freeze
        },
        "candidates_count": len(candidates),
        "candidates": candidates
    }

@router.post("/evaluate-point")
def evaluate_custom_point(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Evaluates rerouting feasibility from arbitrary test coordinates."""
    lat = float(payload.get("latitude", 12.9675))
    lon = float(payload.get("longitude", 79.9427))
    current_temp = float(payload.get("current_temp", 9.4))
    temp_ceiling = float(payload.get("temp_ceiling", 8.0))
    corridor = payload.get("corridor", "NH-48")
    requires_deep_freeze = bool(payload.get("requires_deep_freeze", False))

    candidates = spatial_routing_engine.find_reroute_candidates(
        db=db,
        lat=lat,
        lon=lon,
        requires_deep_freeze=requires_deep_freeze,
        current_temp=current_temp,
        temp_ceiling=temp_ceiling,
        corridor=corridor,
        max_candidates=4
    )

    return {
        "query_coordinates": [lat, lon],
        "candidates": candidates
    }
