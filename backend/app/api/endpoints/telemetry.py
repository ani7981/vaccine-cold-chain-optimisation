from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.all import Shipment, TelemetryReading, Sensor
from app.services.iot.gateway import iot_gateway

router = APIRouter()

class TelemetryPacketSchema(BaseModel):
    shipment_id: Optional[str] = Field(None, description="Target shipment UUID or code")
    shipment_code: Optional[str] = Field(None, description="e.g. VK-1042")
    vehicle_code: Optional[str] = Field(None, description="e.g. TN-4821-HX")
    sensor_code: Optional[str] = Field(None, description="IoT probe logger serial")
    sequence_number: Optional[int] = Field(None, description="Monotonic sequence number for deduplication")
    timestamp: Optional[str] = Field(None, description="ISO-8601 UTC timestamp")
    
    probe_1_temperature: float = Field(..., description="Primary calibrated PT100 temperature in Celsius")
    probe_2_temperature: Optional[float] = Field(None, description="Redundant secondary PT100 probe temperature")
    ambient_temperature: float = Field(28.0, description="External vehicle bay / ambient temperature")
    humidity: float = Field(65.0, description="Relative humidity %")
    
    latitude: float = Field(..., description="WGS84 GPS latitude")
    longitude: float = Field(..., description="WGS84 GPS longitude")
    speed: float = Field(45.0, description="GPS ground speed km/h")
    door_state: str = Field("CLOSED", description="CLOSED | OPEN | SEALED")
    refrigeration_state: str = Field("OPTIMAL", description="OPTIMAL | NORMAL | DEGRADED | FAULT")
    battery_level: Optional[float] = Field(95.0, description="Battery percentage 0-100%")
    signal_strength_dbm: Optional[int] = Field(-65, description="Cellular RSSI in dBm")

@router.post("/ingest")
def ingest_telemetry_packet(
    packet: TelemetryPacketSchema,
    db: Session = Depends(get_db)
):
    """
    Ingests a single IoT sensor packet:
    - Deduplicates retransmissions.
    - Validates dual-probe consensus & flags drift or frozen sensors.
    - Updates running Arrhenius MKT and triggers 4-tier decision engine.
    """
    result = iot_gateway.ingest_packet(db, packet.model_dump())
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("detail"))
    return result

@router.post("/ingest-batch")
def ingest_telemetry_batch(
    packets: List[TelemetryPacketSchema],
    db: Session = Depends(get_db)
):
    """
    Ingests a burst of queued telemetry packets after network reconnect:
    - Reconciles out-of-order jitter arrivals via chronological sorting.
    - Deduplicates retransmissions.
    - Processes kinetic states deterministically.
    """
    raw_packets = [p.model_dump() for p in packets]
    return iot_gateway.ingest_batch(db, raw_packets)

@router.get("/diagnostics/{shipment_id}")
def get_sensor_diagnostics(
    shipment_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns sensor integrity and drift diagnostics for a shipment:
    - Current probe discrepancy |T1 - T2|
    - Historical fault event log
    - Hardware sensor battery and signal levels
    """
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        shipment = db.query(Shipment).filter(Shipment.shipment_code == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    sensor = db.query(Sensor).filter(Sensor.id == shipment.sensor_id).first() if shipment.sensor_id else None

    # Fetch last 30 readings
    readings = db.query(TelemetryReading).filter(
        TelemetryReading.shipment_id == shipment.id
    ).order_by(TelemetryReading.timestamp.desc()).limit(30).all()

    discrepancies = [
        {
            "timestamp": r.timestamp.isoformat(),
            "probe_1": r.probe_1_temperature if r.probe_1_temperature is not None else r.temperature,
            "probe_2": r.probe_2_temperature,
            "discrepancy": r.probe_discrepancy or 0.0,
            "faults": r.sensor_fault_flags or []
        }
        for r in readings
    ]

    # Aggregate recent fault counts
    fault_summary = {}
    for r in readings:
        for f in (r.sensor_fault_flags or []):
            code = f.get("fault_code", "UNKNOWN")
            fault_summary[code] = fault_summary.get(code, 0) + 1

    latest_reading = readings[0] if readings else None

    return {
        "shipment_id": shipment.id,
        "shipment_code": shipment.shipment_code,
        "sensor_id": sensor.id if sensor else None,
        "sensor_code": sensor.sensor_code if sensor else "UNKNOWN",
        "probe_type": sensor.probe_type if sensor else "Dual PT100 Class A + SHT31",
        "calibration_status": sensor.calibration_status if sensor else "VALID",
        "latest_metrics": {
            "battery_level": latest_reading.battery_level if latest_reading else (sensor.battery_level if sensor else 95.0),
            "signal_strength_dbm": latest_reading.signal_strength_dbm if latest_reading else (sensor.signal_strength_dbm if sensor else -65),
            "current_discrepancy": latest_reading.probe_discrepancy if latest_reading else 0.0,
            "is_valid": latest_reading.is_valid if latest_reading else True
        },
        "fault_summary": fault_summary,
        "recent_probe_readings": discrepancies[:10]
    }
