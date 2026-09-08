"""
VaxKavach Telegram Bot — Application entry point.

Lifecycle:
  - Integrated with FastAPI via startup/shutdown lifespan events.
  - Runs in polling mode (no webhook needed for local/demo deployment).
  - The Application instance is stored as app_state.bot_app so the
    notification service can call bot.send_message() directly.
"""
import asyncio
import logging
import os

from telegram.ext import Application

from app.bot.commands import get_handlers

logger = logging.getLogger(__name__)

_bot_app: Application | None = None


def get_bot_app() -> Application | None:
    return _bot_app


async def start_bot() -> None:
    """Initialize and start the Telegram bot in polling mode."""
    global _bot_app
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled.")
        return

    _bot_app = Application.builder().token(token).build()

    for handler in get_handlers():
        _bot_app.add_handler(handler)

    await _bot_app.initialize()
    await _bot_app.start()
    await _bot_app.updater.start_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )
    logger.info("VaxKavach Telegram bot started (polling).")


async def stop_bot() -> None:
    """Gracefully shut down the bot."""
    global _bot_app
    if _bot_app and _bot_app.updater.running:
        await _bot_app.updater.stop()
        await _bot_app.stop()
        await _bot_app.shutdown()
        logger.info("Telegram bot stopped.")
