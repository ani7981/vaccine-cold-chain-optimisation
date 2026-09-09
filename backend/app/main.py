import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # Loads TELEGRAM_BOT_TOKEN and other vars from backend/.env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Telegram bot and simulation engine on FastAPI startup; stop on shutdown."""
    try:
        from app.bot.bot import start_bot
        await start_bot()
    except Exception as exc:
        logger.warning("Telegram bot failed to start (non-fatal): %s", exc)

    try:
        from app.core.database import SessionLocal
        from app.services.simulation.engine import simulation_engine
        db = SessionLocal()
        try:
            simulation_engine.start(db)
            logger.info("Simulation Engine auto-started on server boot.")
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Simulation engine failed to auto-start (non-fatal): %s", exc)

    yield  # ← server is running

    try:
        from app.bot.bot import stop_bot
        await stop_bot()
    except Exception as exc:
        logger.warning("Telegram bot stop error (non-fatal): %s", exc)

    try:
        from app.core.database import SessionLocal
        from app.services.simulation.engine import simulation_engine
        db = SessionLocal()
        try:
            simulation_engine.stop(db)
        finally:
            db.close()
    except Exception as exc:
        logger.warning("Simulation engine stop error: %s", exc)


app = FastAPI(title="VaxKavach API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "VaxKavach"}
