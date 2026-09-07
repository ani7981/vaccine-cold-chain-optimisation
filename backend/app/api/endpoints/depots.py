from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all import Depot

router = APIRouter()

@router.get("/")
def get_depots(db: Session = Depends(get_db)):
    depots = db.query(Depot).all()
    return [{"id": d.id, "name": d.name, "lat": d.latitude, "lon": d.longitude, "services": d.services} for d in depots]
