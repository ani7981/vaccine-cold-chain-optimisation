import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.models.all import Location, Product, Vehicle, Sensor, Shipment

def seed_db():
    db = SessionLocal()
    
    if db.query(Shipment).first():
        print("Database already seeded")
        return
        
    loc1 = Location(id="loc_chennai", name="Chennai Hub", city="Chennai", state="Tamil Nadu", latitude=13.0827, longitude=80.2707, location_type="HUB")
    loc2 = Location(id="loc_vellore", name="Vellore Clinic", city="Vellore", state="Tamil Nadu", latitude=12.9202, longitude=79.1325, location_type="CLINIC")
    db.add(loc1)
    db.add(loc2)
    
    from app.models.all import Depot
    depot1 = Depot(id="depot_kanchi", name="Kanchipuram Backup Store", latitude=12.8341, longitude=79.7036, geom=f"SRID=4326;POINT({79.7036} {12.8341})", services=["REFRIGERATION", "VEHICLE_SWAP"], availability="HIGH", certification_status="VERIFIED")
    depot2 = Depot(id="depot_sriperum", name="Sriperumbudur Hub", latitude=12.9716, longitude=79.9406, geom=f"SRID=4326;POINT({79.9406} {12.9716})", services=["REFRIGERATION"], availability="MEDIUM", certification_status="VERIFIED")
    db.add(depot1)
    db.add(depot2)
    
    prod = Product(id="prod_mr", name="Measles & Rubella Vaccine", temperature_min=2.0, temperature_max=8.0, mkt_limit=8.0, activation_energy=83144.0)
    db.add(prod)
    
    veh = Vehicle(id="veh_001", vehicle_code="TN-01-AB-1234", registration_number="TN-01-AB-1234", refrigeration_status="NORMAL", current_setpoint=3.0, capacity=1000.0)
    db.add(veh)
    
    sensor = Sensor(id="sen_100", sensor_code="SN-VK100", sensor_type="TEMPERATURE_HUMIDITY", firmware_version="1.0.0", calibration_status="VALID")
    db.add(sensor)
    
    db.commit()
    
    shipment = Shipment(
        id="ship_1",
        shipment_code="VK-1042",
        product_id=prod.id,
        origin_location_id=loc1.id,
        destination_location_id=loc2.id,
        vehicle_id=veh.id,
        sensor_id=sensor.id,
        status="ACTIVE",
        temperature_min=2.0,
        temperature_max=8.0,
        mkt_limit=8.0,
        started_at=datetime.now(timezone.utc),
        estimated_arrival=datetime.now(timezone.utc) + timedelta(hours=3),
        current_temperature=3.5,
        current_mkt=3.5
    )
    db.add(shipment)
    
    db.commit()
    db.close()
    print("Seeded database with initial VK-1042 scenario.")

if __name__ == "__main__":
    seed_db()
