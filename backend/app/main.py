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
    """Start the Telegram bot on FastAPI startup; stop it on shutdown."""
    try:
        from app.bot.bot import start_bot
        await start_bot()
    except Exception as exc:
        logger.warning("Telegram bot failed to start (non-fatal): %s", exc)

    yield  # ← server is running

    try:
        from app.bot.bot import stop_bot
        await stop_bot()
    except Exception as exc:
        logger.warning("Telegram bot stop error (non-fatal): %s", exc)


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
