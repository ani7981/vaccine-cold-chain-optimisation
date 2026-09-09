from sqlalchemy.orm import Session
from app.models.all import Depot
from app.services.routing.engine import spatial_routing_engine

def find_nearest_depot(db: Session, lat: float, lon: float):
    """
    Backwards-compatible wrapper:
    Uses PostGIS geodetics & SpatialRoutingEngine to find the optimal facility.
    Returns the SQLAlchemy Depot model instance.
    """
    optimal = spatial_routing_engine.find_optimal_depot(db, lat, lon)
    if optimal:
        return db.query(Depot).filter(Depot.id == optimal["depot_id"]).first()
    
    # Fallback to nearest depot by geodetic distance
    all_depots = db.query(Depot).all()
    if not all_depots:
        return None
    return min(all_depots, key=lambda d: spatial_routing_engine.haversine_km(lat, lon, d.latitude, d.longitude))
