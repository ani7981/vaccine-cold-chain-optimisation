from fastapi import APIRouter
from app.api.endpoints import shipments, analytics, simulation, websocket, audit, fleet, depots, problems
from app.api.endpoints import telegram_users

router = APIRouter()

router.include_router(shipments.router, prefix="/api/shipments", tags=["shipments"])
router.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
router.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
router.include_router(audit.router, prefix="/api/audit", tags=["audit"])
router.include_router(fleet.router, prefix="/api/fleet", tags=["fleet"])
router.include_router(depots.router, prefix="/api/depots", tags=["depots"])
router.include_router(problems.router, prefix="/api/problems", tags=["problems"])
router.include_router(websocket.router, tags=["websocket"])
router.include_router(telegram_users.router, prefix="/telegram", tags=["telegram"])
