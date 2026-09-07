import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base
from datetime import datetime, timezone

class Location(Base):
    __tablename__ = "locations"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    location_type = Column(String)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    mkt_limit = Column(Float)
    activation_energy = Column(Float)
    metadata_config = Column(JSON, default={})

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(String, primary_key=True, index=True)
    vehicle_code = Column(String)
    registration_number = Column(String)
    refrigeration_status = Column(String)
    current_setpoint = Column(Float)
    capacity = Column(Float)

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(String, primary_key=True, index=True)
    sensor_code = Column(String)
    sensor_type = Column(String)
    firmware_version = Column(String)
    calibration_status = Column(String)
    last_seen_at = Column(DateTime(timezone=True))

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(String, primary_key=True, index=True)
    shipment_code = Column(String, index=True)
    product_id = Column(String, ForeignKey("products.id"))
    origin_location_id = Column(String, ForeignKey("locations.id"))
    destination_location_id = Column(String, ForeignKey("locations.id"))
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=True)
    status = Column(String)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    mkt_limit = Column(Float)
    started_at = Column(DateTime(timezone=True))
    estimated_arrival = Column(DateTime(timezone=True))
    current_temperature = Column(Float, nullable=True)
    current_mkt = Column(Float, nullable=True)
    current_problem_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class TelemetryReading(Base):
    __tablename__ = "telemetry_readings"
    id = Column(String, primary_key=True, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id"), index=True)
    timestamp = Column(DateTime(timezone=True), index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    door_state = Column(String)
    ambient_temperature = Column(Float)
    refrigeration_state = Column(String)

class TransitEvent(Base):
    __tablename__ = "transit_events"
    id = Column(String, primary_key=True, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id"), index=True)
    timestamp = Column(DateTime(timezone=True))
    event_type = Column(String)
    status = Column(String)
    duration = Column(Integer)
    event_metadata = Column(JSON, default={})

class Problem(Base):
    __tablename__ = "problems"
    id = Column(String, primary_key=True, index=True)
    problem_code = Column(String, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id"), index=True)
    problem_type = Column(String)
    severity = Column(String)
    status = Column(String)
    detected_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    evidence = Column(JSON, default={})
    rule_results = Column(JSON, default={})

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(String, primary_key=True, index=True)
    problem_id = Column(String, ForeignKey("problems.id"))
    rec_type = Column(String)
    priority = Column(String)
    description = Column(String)
    rationale = Column(String)
    target_depot_id = Column(String, ForeignKey("depots.id"), nullable=True)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    executed_at = Column(DateTime(timezone=True), nullable=True)

class Depot(Base):
    __tablename__ = "depots"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))
    services = Column(JSON, default=[])
    availability = Column(String)
    certification_status = Column(String)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    event_type = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    actor = Column(String)
    payload = Column(JSON, default={})
    previous_hash = Column(String)
    hash = Column(String)

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(String, primary_key=True, index=True, default=lambda: f"sim_{uuid.uuid4().hex[:8]}")
    scenario = Column(String)
    status = Column(String)
    current_tick = Column(Integer, default=0)
    simulation_time = Column(DateTime(timezone=True))
    speed_multiplier = Column(Float, default=1.0)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
