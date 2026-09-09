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
    manufacturer = Column(String, nullable=True)
    doses_per_vial = Column(Integer, default=10)
    batch_default = Column(String, nullable=True)
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
    model = Column(String, nullable=True)
    driver_name = Column(String, nullable=True)
    driver_phone = Column(String, nullable=True)
    status = Column(String, default="HEALTHY")
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    corridor = Column(String, nullable=True)
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
    battery_level = Column(Float, default=95.0)
    signal_strength_dbm = Column(Integer, default=-65)
    probe_type = Column(String, default="Dual PT100 + SHT31")
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
    batch_number = Column(String, nullable=True)
    expiry_date = Column(String, nullable=True)
    doses_count = Column(Integer, default=1000)
    provenance_source = Column(String, default="VERIFIED_OFFICIAL_IOT")
    is_simulated = Column(Boolean, default=False)
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
    probe_1_temperature = Column(Float, nullable=True)
    probe_2_temperature = Column(Float, nullable=True)
    probe_discrepancy = Column(Float, nullable=True)
    sequence_number = Column(Integer, nullable=True)
    humidity = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    door_state = Column(String)
    ambient_temperature = Column(Float)
    refrigeration_state = Column(String)
    battery_level = Column(Float, nullable=True)
    signal_strength_dbm = Column(Integer, nullable=True)
    sensor_fault_flags = Column(JSON, default=[])
    is_valid = Column(Boolean, default=True)

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
    resolution_reason = Column(String, nullable=True)
    corrective_action = Column(String, nullable=True)
    resolution_notes = Column(String, nullable=True)
    resolved_by_user = Column(String, nullable=True)
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

class AuditBlock(Base):
    __tablename__ = "audit_blocks"
    id = Column(String, primary_key=True, index=True)
    block_index = Column(Integer, unique=True, index=True, nullable=False)
    merkle_root = Column(String, index=True, nullable=False)
    event_count = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    previous_block_hash = Column(String, nullable=False)
    block_hash = Column(String, nullable=False)
    sealed_at = Column(DateTime(timezone=True), nullable=False)
    signer_identity = Column(String, nullable=False)

class ComplianceCertificate(Base):
    __tablename__ = "compliance_certificates"
    id = Column(String, primary_key=True, index=True)
    certificate_id = Column(String, unique=True, index=True, nullable=False)
    shipment_id = Column(String, ForeignKey("shipments.id"), index=True, nullable=False)
    batch_number = Column(String, nullable=False)
    vaccine_name = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    doses_count = Column(Integer, nullable=False)
    departure_depot = Column(String, nullable=False)
    destination_depot = Column(String, nullable=False)
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    arrived_at = Column(DateTime(timezone=True), nullable=True)
    total_transit_hours = Column(Float, nullable=True)
    mean_kinetic_temperature_c = Column(Float, nullable=False)
    mkt_allowable_limit_c = Column(Float, nullable=False)
    thermal_compliance_status = Column(String, nullable=False)
    excursion_duration_minutes = Column(Integer, nullable=False)
    sensor_probe_fault_count = Column(Integer, nullable=False)
    merkle_root_seal = Column(String, nullable=False)
    verified_by_role = Column(String, nullable=False)
    regulatory_standard = Column(String, nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=False)
    dossier_json = Column(JSON, nullable=True)

