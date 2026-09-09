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

    # Register bot commands and enable persistent Menu popup button
    try:
        from telegram import BotCommand, MenuButtonCommands
        commands = [
            BotCommand("start", "Start VaxKavach bot & main control hub"),
            BotCommand("help", "View full interactive guide & command list"),
            BotCommand("shipments", "Active consignments, temperatures & status"),
            BotCommand("fleet", "Live reefer fleet locations, speed & corridors"),
            BotCommand("shipment", "Inspect specific consignment (e.g. /shipment VK-1042)"),
            BotCommand("problems", "Active cold-chain incidents & excursions queue"),
            BotCommand("critical", "High priority alerts requiring emergency triage"),
            BotCommand("ai", "XGBoost ML spoilage risk, +4h forecast & SHAP"),
            BotCommand("aimodel", "AI model architecture, ROC-AUC & metrics"),
            BotCommand("aisim", "Simulate counterfactual What-If scenarios"),
            BotCommand("events", "Live chronological audit event stream"),
            BotCommand("audit", "Verify Merkle tree root & tamper-proof ledger"),
            BotCommand("admin", "Admin command console & diagnostic health checks"),
            BotCommand("chaos", "Simulate synthetic field failure scenarios"),
            BotCommand("clear_chaos", "Clear all active chaos injection stress tests"),
        ]
        await _bot_app.bot.set_my_commands(commands)
        await _bot_app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
        logger.info("Successfully registered %d Telegram bot commands and menu button.", len(commands))
    except Exception as exc:
        logger.warning("Failed to register Telegram bot commands: %s", exc)

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
