# -*- coding: utf-8 -*-
"""
VaxKavach — Telegram Notification Service

Called by the FastAPI layer to push rich, detailed alert cards
to registered operators and supervisors.
"""
import logging
import os
from typing import Any

from app.bot.formatters import format_problem_card
from app.bot.keyboards import critical_alert_keyboard, problem_action_keyboard

logger = logging.getLogger(__name__)


async def _get_supervisor_chat_ids() -> list[int]:
    """
    Return Telegram chat_ids of all configured operators/supervisors.
    Reads from TELEGRAM_NOTIFY_CHAT_IDS (comma-separated integers).
    """
    raw = os.getenv("TELEGRAM_NOTIFY_CHAT_IDS", "")
    ids = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return ids


async def notify_critical_alert(problem: dict[str, Any]) -> None:
    """
    Send an industrial-grade critical thermal breach card to all supervisors.
    """
    from app.bot.bot import get_bot_app

    bot_app = get_bot_app()
    if not bot_app:
        logger.debug("Bot not running — skipping notification.")
        return

    chat_ids = await _get_supervisor_chat_ids()
    if not chat_ids:
        logger.debug("No TELEGRAM_NOTIFY_CHAT_IDS configured — skipping.")
        return

    code = problem.get("problem_code") or problem.get("id") or "?"
    ship_code = problem.get("shipment_code") or problem.get("shipment_id") or "?"
    text = format_problem_card(problem)
    keyboard = critical_alert_keyboard(problem["id"], ship_code)

    for chat_id in chat_ids:
        try:
            await bot_app.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            logger.info("Critical alert card delivered to chat_id=%s for problem=%s", chat_id, code)
        except Exception as exc:
            logger.error("Failed to notify chat_id=%s: %s", chat_id, exc)


async def notify_warning_alert(problem: dict[str, Any]) -> None:
    """
    Send a predictive warning alert card when thermal drift or threshold approach is detected.
    """
    from app.bot.bot import get_bot_app

    bot_app = get_bot_app()
    if not bot_app:
        return

    chat_ids = await _get_supervisor_chat_ids()
    if not chat_ids:
        return

    ship_code = problem.get("shipment_code") or problem.get("shipment_id") or "?"
    text = format_problem_card(problem)
    keyboard = problem_action_keyboard(problem["id"], ship_code, severity="WARNING")

    for chat_id in chat_ids:
        try:
            await bot_app.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
        except Exception as exc:
            logger.error("Failed to deliver warning to chat_id=%s: %s", chat_id, exc)


async def notify_incident_resolved(problem: dict[str, Any]) -> None:
    """
    Send a high-craft resolution receipt when an incident is marked RESOLVED.
    """
    from app.bot.bot import get_bot_app

    bot_app = get_bot_app()
    if not bot_app:
        return

    chat_ids = await _get_supervisor_chat_ids()
    if not chat_ids:
        return

    code = problem.get("problem_code") or problem.get("id") or "?"
    ship_code = problem.get("shipment_code") or problem.get("shipment_id") or "?"
    resolved_by = problem.get("resolved_by_user") or "Authorized Operator"
    reason = problem.get("resolution_reason") or "Cold chain re-stabilization"
    notes = problem.get("resolution_notes") or "Temperature restored to safe 2.0°C-8.0°C envelope."

    text = (
        f"✅ [INCIDENT RESOLVED — COMPLIANCE RESTORED]\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Incident Code: `{code}`\n"
        f"📦 Shipment: `{ship_code}`\n"
        f"👤 Resolved by: *{resolved_by}*\n"
        f"📋 Corrective Reason: _{reason}_\n"
        f"📝 Field Notes: _{notes}_\n"
        f"🛡 Standard: WHO-PQS Verification Active\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    )

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("📦 INSPECT SHIPMENT", callback_data=f"shipment:{ship_code}"),
        InlineKeyboardButton("🌐 DASHBOARD", url=f"http://127.0.0.1:5173/shipment.html?id={ship_code}"),
    ]])

    for chat_id in chat_ids:
        try:
            await bot_app.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=kb,
            )
        except Exception as exc:
            logger.error("Failed to send resolution notice to chat_id=%s: %s", chat_id, exc)
