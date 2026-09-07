from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.all import Depot

def find_nearest_depot(db: Session, lat: float, lon: float):
    # PostGIS distance between depot geom and the given point
    # ST_MakePoint takes (lon, lat)
    point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    
    # ST_Distance calculates distance. For geography it would be meters, 
    # but we are using geometry srid=4326, so it's degrees.
    # To get meters, we can cast to geography or just order by distance.
    query = select(Depot).order_by(
        func.ST_Distance(Depot.geom, point)
    ).limit(1)
    
    result = db.execute(query).scalar_one_or_none()
    return result
