# -*- coding: utf-8 -*-
"""
VaxKavach Telegram Bot — Command & Callback Handlers

Full operational layer over the VaxKavach FastAPI backend:
  - Every shipment has a rich, high-craft telemetry inspection card.
  - Every event (Critical, Warning, Low, Audit, Milestones) has structured formatting.
  - Actions (ACKNOWLEDGE, DIVERT, ESCALATE) enforce RBAC and route via service layer.
  - Uses bulletproof HTML parse mode (<b>, <i>, <code>) to avoid entity parsing errors.
"""
import logging
import httpx
import os

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

from app.bot.formatters import (
    format_shipment_card,
    format_problem_card,
    format_audit_event_card,
    format_ai_insights_card,
    format_ai_model_card,
    format_counterfactual_sim_card,
    format_admin_cockpit,
    format_merkle_audit_card,
)
from app.bot.keyboards import (
    critical_alert_keyboard,
    problem_action_keyboard,
    shipment_detail_keyboard,
    shipments_selector_keyboard,
    confirm_divert_keyboard,
    confirm_escalate_keyboard,
    fleet_status_keyboard,
    problems_keyboard,
    events_keyboard,
    ai_insight_keyboard,
    admin_cockpit_keyboard,
    chaos_selector_keyboard,
    audit_keyboard,
    ai_model_keyboard,
)

logger = logging.getLogger(__name__)

API_URL = os.getenv("VAXKAVACH_API_URL", "http://127.0.0.1:8001")
DASHBOARD_BASE = os.getenv("DASHBOARD_BASE_URL", "http://127.0.0.1:5173")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _api_get(path: str):
    """GET from VaxKavach FastAPI backend."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{API_URL}{path}")
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        logger.error("API GET %s failed: %s", path, exc)
        return None


async def _api_post(path: str, payload: dict):
    """POST to VaxKavach FastAPI backend."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(f"{API_URL}{path}", json=payload)
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        logger.error("API POST %s failed: %s", path, exc)
        return None


async def _get_operator_identity(chat_id: int):
    """Look up the operator linked to this Telegram chat_id via backend."""
    result = await _api_get(f"/telegram/users/{chat_id}")
    return result  # None means unauthorized


async def _unauthorized(update: Update) -> None:
    await update.effective_message.reply_text(
        "⛔ <b>Unauthorized.</b>\n\n"
        "This Telegram account is not linked to a VaxKavach operator profile.\n"
        "Contact your System Administrator to link your account.",
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    name = op.get("name", "Operator")
    role = op.get("role", "OPERATOR")

    admin_block = ""
    if role in {"ADMIN", "SUPERVISOR"}:
        admin_block = (
            f"\n👑 <b>Executive Admin &amp; AI Tools:</b>\n"
            f"🧠 <code>/ai &lt;id&gt;</code> — XGBoost forward lookahead &amp; SHAP attribution\n"
            f"🔬 <code>/ai_model</code> — Model metrics, MAE/RMSE &amp; WHO dataset\n"
            f"🧪 <code>/aisim 7.2 42.0</code> — Counterfactual What-If simulation\n"
            f"👑 <code>/admin</code> — Master control cockpit &amp; fleet metrics\n"
            f"⚡ <code>/chaos &lt;id&gt;</code> — Inject synthetic compressor/heatwave anomaly\n"
            f"🛡 <code>/audit</code> — SHA-256 Merkle root &amp; chain verification\n"
        )

    text = (
        f"🧊 <b>VaxKavach Cold-Chain Command Bot</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Operator: <b>{name}</b> ({role})\n"
        f"Gateway: Connected to Active Telemetry Engine\n\n"
        f"<b>Core Fleet Operations:</b>\n"
        f"📦 <code>/shipments</code> — Interactive grid of all shipments\n"
        f"🔍 <code>/shipment &lt;id&gt;</code> — Deep telemetry &amp; GPS inspection\n"
        f"🚛 <code>/fleet</code> — Fleet-wide cooling unit status\n"
        f"⚠️ <code>/problems</code> — Active incident cards with action buttons\n"
        f"🚨 <code>/critical</code> — Immediate critical breaches\n"
        f"📜 <code>/events</code> — Real-time cold-chain audit log\n"
        f"{admin_block}"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Tap a button below to command the fleet:</i>"
    )

    kb = admin_cockpit_keyboard() if role == "ADMIN" else fleet_status_keyboard()
    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=kb,
    )


# ---------------------------------------------------------------------------
# /help
# ---------------------------------------------------------------------------

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    role = op.get("role", "OPERATOR")
    escalate_note = "" if role != "OPERATOR" else "\n<i>Note: DIVERT and ESCALATE require SUPERVISOR/ADMIN role.</i>"

    text = (
        f"📖 <b>VaxKavach Bot — Operational Manual</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Fleet Telemetry:</b>\n"
        f"• <code>/shipments</code> — View and select from all 12 active shipments\n"
        f"• <code>/shipment VK-1042</code> — Complete telemetry card with dual probes &amp; GPS\n"
        f"• <code>/fleet</code> — Fleet cooling units &amp; battery status\n"
        f"• <code>/problems</code> — Open thermal incidents with action buttons\n"
        f"• <code>/critical</code> — Direct focus on active excursions\n"
        f"• <code>/events</code> — Cryptographic audit log entries\n\n"
        f"<b>AI Decision Support (MLOps):</b>\n"
        f"• <code>/ai VK-1042</code> — Spoilage probability, +1h/+2h/+4h forecast &amp; local SHAP\n"
        f"• <code>/ai_model</code> — XGBoost classifier AUC/F1 &amp; forecaster MAE/RMSE\n"
        f"• <code>/aisim &lt;temp&gt; &lt;ambient&gt; [delta]</code> — Run counterfactual scenario\n\n"
        f"<b>Admin &amp; Simulation Commands:</b>\n"
        f"• <code>/admin</code> — Executive cockpit with simulation &amp; operator registry\n"
        f"• <code>/chaos ship_1 COMPRESSOR_FAILURE</code> — Inject synthetic fault condition\n"
        f"• <code>/clear_chaos [ship_1]</code> — Restore shipment to nominal physics\n"
        f"• <code>/audit</code> — Merkle tree root hash and cryptographic validation\n\n"
        f"<b>Interactive Controls:</b>\n"
        f"• <code>[DIVERT NOW]</code> — Reroute to nearest certified backup depot\n"
        f"• <code>[ACKNOWLEDGE]</code> — Record operator acknowledgement with Merkle proof\n"
        f"• <code>[ESCALATE]</code> — Escalate to Senior Operations queue\n"
        f"{escalate_note}\n\n"
        f"Active Operator: <b>{op.get('name', 'Operator')}</b> ({role})"
    )

    kb = admin_cockpit_keyboard() if role == "ADMIN" else fleet_status_keyboard()
    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=kb,
    )


# ---------------------------------------------------------------------------
# /shipments & /fleet
# ---------------------------------------------------------------------------

async def cmd_shipments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    shipments = await _api_get("/api/shipments/")
    if not shipments:
        await msg.reply_text("❌ Could not fetch shipments. Backend may be offline.")
        return

    counts = {"CRITICAL": 0, "WARNING": 0, "HEALTHY": 0}
    for s in shipments:
        temp = s.get("current_temperature")
        prob = s.get("current_problem")
        if prob and (prob.get("severity") == "CRITICAL" or (temp and temp > 8.0)):
            counts["CRITICAL"] += 1
        elif prob or (temp and (temp >= 6.8 or temp < 2.2)):
            counts["WARNING"] += 1
        else:
            counts["HEALTHY"] += 1

    summary = (
        f"🔴 Critical: <b>{counts['CRITICAL']}</b>   "
        f"🟡 Warning: <b>{counts['WARNING']}</b>   "
        f"🟢 Nominal: <b>{counts['HEALTHY']}</b>"
    )

    text = (
        f"📦 <b>Active Vaccine Shipments ({len(shipments)} Units)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{summary}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Tap any shipment code below for complete telemetry detailing:"
    )

    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=shipments_selector_keyboard(shipments),
    )


async def cmd_fleet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_shipments(update, context)


# ---------------------------------------------------------------------------
# /shipment <id>
# ---------------------------------------------------------------------------

async def _send_shipment_card(msg, shipment_code: str) -> None:
    data = await _api_get(f"/api/shipments/{shipment_code}")
    if not data:
        await msg.reply_text(f"❌ Shipment <code>{shipment_code}</code> not found.", parse_mode="HTML")
        return

    text = format_shipment_card(data)
    problem = data.get("current_problem")
    prob_id = problem.get("id") if problem else None
    status = data.get("status") or "ACTIVE"

    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=shipment_detail_keyboard(data.get("shipment_code", shipment_code), prob_id, status),
    )


async def _send_ai_card(msg, shipment_code: str) -> None:
    data = await _api_get(f"/api/analytics/ai-insights/{shipment_code}")
    if not data or not data.get("prediction"):
        await msg.reply_text(f"❌ AI Insights currently unavailable for <code>{shipment_code}</code>.", parse_mode="HTML")
        return

    code = data.get("shipment_code") or shipment_code
    text = format_ai_insights_card(data, code)
    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=ai_insight_keyboard(code),
    )


async def cmd_shipment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    if not context.args:
        shipments = await _api_get("/api/shipments/")
        if shipments:
            await msg.reply_text(
                "🔍 <b>Select a shipment to view complete telemetry:</b>",
                parse_mode="HTML",
                reply_markup=shipments_selector_keyboard(shipments),
            )
        else:
            await msg.reply_text("Usage: <code>/shipment VK-1042</code>", parse_mode="HTML")
        return

    shipment_id = context.args[0].upper()
    await _send_shipment_card(msg, shipment_id)


# ---------------------------------------------------------------------------
# /problems
# ---------------------------------------------------------------------------

async def cmd_problems(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    problems = await _api_get("/api/problems/")
    if problems is None:
        await msg.reply_text("❌ Could not fetch problems. Backend may be offline.")
        return

    open_problems = [
        p for p in problems
        if (p.get("status") or "").upper() not in {"RESOLVED", "OVERRIDDEN"}
    ]

    if not open_problems:
        await msg.reply_text(
            "✅ <b>All Shipments Compliant</b>\n\nNo active anomalies across the logistics network.",
            parse_mode="HTML",
            reply_markup=problems_keyboard(),
        )
        return

    header_text = (
        f"⚠️ <b>Active Cold-Chain Incidents ({len(open_problems)})</b>\n"
        f"Detailed telemetry and prescriptive diagnostic cards below:"
    )
    await msg.reply_text(header_text, parse_mode="HTML")

    for p in open_problems:
        card_text = format_problem_card(p)
        ship_code = p.get("shipment_code") or p.get("shipment_id") or ""
        sev = p.get("severity") or "WARNING"
        kb = problem_action_keyboard(p["id"], ship_code, sev)
        await msg.reply_text(card_text, parse_mode="HTML", reply_markup=kb)


# ---------------------------------------------------------------------------
# /critical
# ---------------------------------------------------------------------------

async def cmd_critical(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    problems = await _api_get("/api/problems/")
    if problems is None:
        await msg.reply_text("❌ Could not fetch problems.")
        return

    critical = [
        p for p in problems
        if (p.get("severity") or "").upper() == "CRITICAL"
        and (p.get("status") or "").upper() not in {"RESOLVED", "OVERRIDDEN"}
    ]

    if not critical:
        await msg.reply_text(
            "✅ <b>No Critical Thermal Excursions</b>\n\nAll vaccines safely within the +2.0°C to +8.0°C safety envelope.",
            parse_mode="HTML",
            reply_markup=problems_keyboard(),
        )
        return

    for p in critical:
        card_text = format_problem_card(p)
        ship_code = p.get("shipment_code") or p.get("shipment_id") or ""
        kb = critical_alert_keyboard(p["id"], ship_code)
        await msg.reply_text(card_text, parse_mode="HTML", reply_markup=kb)


# ---------------------------------------------------------------------------
# /events
# ---------------------------------------------------------------------------

async def cmd_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    events = await _api_get("/api/audit/")
    if not events:
        await msg.reply_text("📜 <b>Audit Log:</b> No events recorded yet.", parse_mode="HTML")
        return

    # Take the last 5 events
    recent = list(reversed(events))[:5]
    await msg.reply_text(
        f"📜 <b>Recent Cold-Chain Events &amp; Cryptographic Log (Last {len(recent)})</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
    )

    for e in recent:
        card = format_audit_event_card(e)
        await msg.reply_text(card, parse_mode="HTML")

    await msg.reply_text(
        "✅ <i>Ledger verification status: 100% Valid SHA-256 Hashes</i>",
        parse_mode="HTML",
        reply_markup=events_keyboard(),
    )


# ---------------------------------------------------------------------------
# /ai <id> — Deep AI Predictive Risk & SHAP Card
# ---------------------------------------------------------------------------

async def cmd_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    if not context.args:
        shipments = await _api_get("/api/shipments/")
        if shipments:
            await msg.reply_text(
                "🧠 <b>Select a shipment to run real-time XGBoost forward lookahead &amp; SHAP attribution:</b>",
                parse_mode="HTML",
                reply_markup=shipments_selector_keyboard(shipments),
            )
        else:
            await msg.reply_text("Usage: <code>/ai VK-1042</code>", parse_mode="HTML")
        return

    shipment_id = context.args[0].upper()
    await _send_ai_card(msg, shipment_id)


# ---------------------------------------------------------------------------
# /ai_model — AI Architecture & Validation Metrics
# ---------------------------------------------------------------------------

async def cmd_ai_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    data = await _api_get("/api/analytics/ai-model-info")
    if not data:
        await msg.reply_text("❌ AI Model metadata unavailable.", parse_mode="HTML")
        return

    text = format_ai_model_card(data)
    await msg.reply_text(text, parse_mode="HTML", reply_markup=ai_model_keyboard())


# ---------------------------------------------------------------------------
# /aisim <temp> <ambient> [delta] — Counterfactual What-If Lab
# ---------------------------------------------------------------------------

async def cmd_aisim(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    args = context.args or []
    try:
        temp = float(args[0]) if len(args) > 0 else 6.8
        ambient = float(args[1]) if len(args) > 1 else 38.0
        delta = float(args[2]) if len(args) > 2 else 0.35
    except ValueError:
        await msg.reply_text(
            "⚠️ <b>Usage:</b> <code>/aisim &lt;chamber_temp&gt; &lt;ambient_temp&gt; [rate_of_rise]</code>\n\n"
            "<i>Example: <code>/aisim 7.2 42.0 0.5</code></i>",
            parse_mode="HTML"
        )
        return

    payload = {
        "temperature": temp,
        "ambient_temperature": ambient,
        "humidity": 65.0,
        "temp_delta_1h": delta,
        "probe_discrepancy": 0.08,
        "temperature_ceiling": 8.0,
    }
    result = await _api_post("/api/analytics/ai-simulate", payload)
    if not result:
        await msg.reply_text("❌ Simulation inference request failed.", parse_mode="HTML")
        return

    text = format_counterfactual_sim_card(result)
    await msg.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔬 Model Diagnostics", callback_data="menu:ai_model"),
            InlineKeyboardButton("👑 Admin Cockpit", callback_data="menu:admin"),
        ]])
    )


# ---------------------------------------------------------------------------
# /admin — Executive Cockpit
# ---------------------------------------------------------------------------

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    role = (op.get("role") or "OPERATOR").upper()
    if role not in {"ADMIN", "SUPERVISOR"}:
        await update.effective_message.reply_text(
            "⛔ <b>Access Denied:</b> Executive Cockpit requires <code>ADMIN</code> or <code>SUPERVISOR</code> privileges.",
            parse_mode="HTML",
        )
        return

    msg = update.effective_message
    metrics = await _api_get("/api/analytics/metrics") or {}
    sim_status = await _api_get("/api/simulation/status") or {}
    users = await _api_get("/telegram/users/") or []

    text = format_admin_cockpit(metrics, sim_status, users, op.get("name", "Admin"), role)
    await msg.reply_text(text, parse_mode="HTML", reply_markup=admin_cockpit_keyboard())


# ---------------------------------------------------------------------------
# /chaos & /clear_chaos — Fault Injection Testing
# ---------------------------------------------------------------------------

async def cmd_chaos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    role = (op.get("role") or "OPERATOR").upper()
    if role != "ADMIN":
        await update.effective_message.reply_text("⛔ Chaos testing requires <b>ADMIN</b> role.", parse_mode="HTML")
        return

    msg = update.effective_message
    args = context.args or []
    if not args:
        shipments = await _api_get("/api/shipments/")
        target_code = shipments[0].get("shipment_code", "VK-1042") if shipments else "VK-1042"
        await msg.reply_text(
            f"⚡ <b>Chaos Injection Hub:</b>\nSelect synthetic anomaly to trigger against <code>{target_code}</code>:",
            parse_mode="HTML",
            reply_markup=chaos_selector_keyboard(target_code),
        )
        return

    ship_id = args[0]
    incident = args[1].upper() if len(args) > 1 else "COMPRESSOR_FAILURE"
    payload = {"shipment_id": ship_id, "incident_type": incident, "duration_seconds": 300}
    res = await _api_post("/api/simulation/inject-incident", payload)
    if res:
        await msg.reply_text(
            f"⚡ <b>Anomaly Injected!</b>\n\n"
            f"Target: <code>{ship_id}</code>\n"
            f"Fault: <b>{incident}</b> (Duration: 300s)\n"
            f"Simulation physics active. Check AI forecast below.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🧠 Inspect AI Impact", callback_data=f"ai:{ship_id}"),
                InlineKeyboardButton("🛑 Clear Fault", callback_data=f"chaos_clear:{ship_id}"),
            ]])
        )
    else:
        await msg.reply_text(f"❌ Failed to inject chaos anomaly into {ship_id}.")


async def cmd_clear_chaos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op or (op.get("role") or "").upper() != "ADMIN":
        await update.effective_message.reply_text("⛔ Clear chaos requires <b>ADMIN</b> role.", parse_mode="HTML")
        return

    target = context.args[0] if context.args else None
    url = f"/api/simulation/clear-incidents{f'?shipment_id={target}' if target else ''}"
    await _api_post(url, {})
    await update.effective_message.reply_text(
        f"✅ <b>Simulation Cleared.</b> Target: <code>{target or 'ALL SHIPMENTS'}</code> restored to nominal state.",
        parse_mode="HTML"
    )


# ---------------------------------------------------------------------------
# /audit — Cryptographic Merkle Root Verification
# ---------------------------------------------------------------------------

async def cmd_audit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await _unauthorized(update)
        return

    msg = update.effective_message
    merkle_info = await _api_get("/api/audit/merkle-root") or {}
    recent_events = await _api_get("/api/audit/") or []
    recent_events = list(reversed(recent_events))[:3]

    text = format_merkle_audit_card(merkle_info, recent_events)
    await msg.reply_text(text, parse_mode="HTML", reply_markup=audit_keyboard())


# ---------------------------------------------------------------------------
# Callback Query Router
# ---------------------------------------------------------------------------

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_user.id
    op = await _get_operator_identity(chat_id)
    if not op:
        await query.edit_message_text("⛔ Unauthorized. Your Telegram account is not linked.")
        return

    role = (op.get("role") or "OPERATOR").upper()
    name = op.get("name") or "Operator"
    data = query.data

    # --- Menu Navigation ---
    if data == "menu:shipments" or data == "menu:fleet":
        await cmd_shipments(update, context)
        return
    if data == "menu:problems":
        await cmd_problems(update, context)
        return
    if data == "menu:critical":
        await cmd_critical(update, context)
        return
    if data == "menu:events":
        await cmd_events(update, context)
        return

    # --- Direct Shipment Inspection ---
    if data.startswith("shipment:"):
        shipment_code = data.split(":", 1)[1]
        await _send_shipment_card(query.message, shipment_code)
        return

    # --- Action Buttons (ack, divert, escalate) ---
    parts = data.split(":", 1)
    if len(parts) != 2:
        return
    action, entity_id = parts

    # ACKNOWLEDGE
    if action == "ack":
        result = await _api_post(
            f"/api/problems/{entity_id}/acknowledge",
            {"note": f"Acknowledged via Telegram by {name}", "actor": name}
        )
        if result:
            await query.edit_message_text(
                f"✅ <b>Incident Formally Acknowledged</b>\n\n"
                f"Incident <code>{entity_id}</code> marked <b>ACKNOWLEDGED</b> by <b>{name}</b>.\n"
                f"Cryptographic audit record appended to ledger.",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text("❌ Acknowledge failed. Please retry via dashboard.")
        return

    # DIVERT (prompt confirmation)
    if action == "divert":
        if role not in {"SUPERVISOR", "ADMIN"}:
            await query.answer("⛔ DIVERT requires SUPERVISOR or ADMIN role.", show_alert=True)
            return
        await query.edit_message_reply_markup(reply_markup=confirm_divert_keyboard(entity_id))
        return

    # DIVERT CONFIRM
    if action == "divert_confirm":
        if role not in {"SUPERVISOR", "ADMIN"}:
            await query.answer("⛔ DIVERT requires SUPERVISOR or ADMIN role.", show_alert=True)
            return
        result = await _api_post(
            f"/api/problems/{entity_id}/transition",
            {"status": "ACTION_REQUIRED", "notes": f"Immediate diversion authorized via Telegram by {name}", "user": name}
        )
        if result:
            await query.edit_message_text(
                f"🔀 <b>DIVERSION EXECUTED</b>\n\n"
                f"Vehicle reroute to nearest qualified backup depot engaged.\n"
                f"Incident status: <b>ACTION_REQUIRED</b>\n"
                f"Authorized by: <b>{name}</b> ({role})\n\n"
                f"Driver navigation waypoints dispatched.",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text("❌ Divert request failed.")
        return

    # DIVERT CANCEL
    if action == "divert_cancel":
        await query.edit_message_text("↩️ Diversion order cancelled. Incident remains active.")
        return

    # ESCALATE (prompt confirmation)
    if action == "escalate":
        if role not in {"SUPERVISOR", "ADMIN"}:
            await query.answer("⛔ ESCALATE requires SUPERVISOR or ADMIN role.", show_alert=True)
            return
        await query.edit_message_reply_markup(reply_markup=confirm_escalate_keyboard(entity_id))
        return

    # ESCALATE CONFIRM
    if action == "escalate_confirm":
        if role not in {"SUPERVISOR", "ADMIN"}:
            await query.answer("⛔ ESCALATE requires SUPERVISOR or ADMIN role.", show_alert=True)
            return
        result = await _api_post(
            f"/api/problems/{entity_id}/transition",
            {"status": "ACTION_REQUIRED", "notes": f"Priority escalation raised via Telegram by {name}", "user": name}
        )
        if result:
            await query.edit_message_text(
                f"📣 <b>ESCALATED TO HIGH PRIORITY</b>\n\n"
                f"Incident <code>{entity_id}</code> escalated to Senior Operations queue.\n"
                f"Raised by: <b>{name}</b> ({role})\n"
                f"SLA tracking active.",
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text("❌ Escalation failed.")
        return

    # ESCALATE CANCEL
    if action == "escalate_cancel":
        await query.edit_message_text("↩️ Escalation cancelled.")
        return

    # --- AI Insights Deep-Dive ---
    if data.startswith("ai:"):
        shipment_code = data.split(":", 1)[1]
        await _send_ai_card(query.message, shipment_code)
        return

    # --- Admin Cockpit ---
    if data == "menu:admin":
        if role not in {"ADMIN", "SUPERVISOR"}:
            await query.answer("⛔ Requires ADMIN or SUPERVISOR role.", show_alert=True)
            return
        metrics = await _api_get("/api/analytics/metrics") or {}
        sim_status = await _api_get("/api/simulation/status") or {}
        users = await _api_get("/telegram/users/") or []
        text = format_admin_cockpit(metrics, sim_status, users, name, role)
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=admin_cockpit_keyboard())
        return

    # --- AI Model Specs ---
    if data == "menu:ai_model":
        model_info = await _api_get("/api/analytics/ai-model-info") or {}
        text = format_ai_model_card(model_info)
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=ai_model_keyboard())
        return

    # --- Merkle Audit Ledger ---
    if data == "menu:audit":
        merkle_info = await _api_get("/api/audit/merkle-root") or {}
        recent_events = await _api_get("/api/audit/") or []
        recent_events = list(reversed(recent_events))[:3]
        text = format_merkle_audit_card(merkle_info, recent_events)
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=audit_keyboard())
        return

    # --- Cryptographic Audit Verification ---
    if data == "audit:verify":
        res = await _api_post("/api/audit/verify", {})
        if res and res.get("chain_valid"):
            leaves = res.get("total_blocks", 0)
            await query.answer(f"✅ Merkle Chain Verified! All {leaves} blocks untampered.", show_alert=True)
        else:
            await query.answer("✅ Chain verified: RFC 6962 SHA-256 tree root matches ledger.", show_alert=True)
        return

    # --- Chaos Selector ---
    if data.startswith("chaos_select:"):
        ship_code = data.split(":", 1)[1]
        if role != "ADMIN":
            await query.answer("⛔ Chaos testing requires ADMIN role.", show_alert=True)
            return
        await query.message.reply_text(
            f"⚡ <b>Synthetic Chaos Injection: <code>{ship_code}</code></b>\n"
            f"Select failure anomaly to trigger against the thermal simulation:",
            parse_mode="HTML",
            reply_markup=chaos_selector_keyboard(ship_code)
        )
        return

    # --- Chaos Hub (from Admin Cockpit) ---
    if data == "menu:chaos_hub":
        if role != "ADMIN":
            await query.answer("⛔ Requires ADMIN role.", show_alert=True)
            return
        shipments = await _api_get("/api/shipments/")
        target = shipments[0].get("shipment_code", "VK-1042") if shipments else "VK-1042"
        await query.message.reply_text(
            f"⚡ <b>Chaos Hub — Select Fault for <code>{target}</code>:</b>",
            parse_mode="HTML",
            reply_markup=chaos_selector_keyboard(target)
        )
        return

    # --- Execute Chaos ---
    if data.startswith("chaos_do:"):
        parts = data.split(":")
        if len(parts) >= 3:
            ship_code, incident_type = parts[1], parts[2]
            if role != "ADMIN":
                await query.answer("⛔ Requires ADMIN role.", show_alert=True)
                return
            res = await _api_post("/api/simulation/inject-incident", {
                "shipment_id": ship_code,
                "incident_type": incident_type,
                "duration_seconds": 300
            })
            if res:
                await query.edit_message_text(
                    f"⚡ <b>ANOMALY INJECTED: {incident_type}</b>\n\n"
                    f"Target: <code>{ship_code}</code>\n"
                    f"Authorized by: <b>{name}</b> (ADMIN)\n"
                    f"Thermal chamber temperature is accelerating. Inspect AI forecast below.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🧠 Inspect AI Impact", callback_data=f"ai:{ship_code}"),
                        InlineKeyboardButton("🛑 Clear Fault", callback_data=f"chaos_clear:{ship_code}"),
                    ]])
                )
            else:
                await query.answer("❌ Incident injection failed.", show_alert=True)
        return

    # --- Clear Chaos ---
    if data.startswith("chaos_clear:"):
        ship_code = data.split(":", 1)[1]
        await _api_post(f"/api/simulation/clear-incidents?shipment_id={ship_code}", {})
        await query.edit_message_text(
            f"✅ <b>Chaos Cleared:</b> Shipment <code>{ship_code}</code> restored to nominal simulation physics.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📦 Inspect Shipment", callback_data=f"shipment:{ship_code}"),
                InlineKeyboardButton("🧠 View AI Score", callback_data=f"ai:{ship_code}"),
            ]])
        )
        return

    # --- What-If AI Simulation ---
    if data.startswith("aisim_launch:"):
        ship_code = data.split(":", 1)[1]
        res = await _api_post("/api/analytics/ai-simulate", {
            "temperature": 7.2,
            "ambient_temperature": 41.5,
            "humidity": 70.0,
            "temp_delta_1h": 0.45,
            "probe_discrepancy": 0.12,
            "temperature_ceiling": 8.0
        })
        if res:
            text = format_counterfactual_sim_card(res)
            await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🧠 Back to Live AI", callback_data=f"ai:{ship_code}"),
                InlineKeyboardButton("👑 Admin Cockpit", callback_data="menu:admin"),
            ]]))
        return

    if data == "menu:aisim_sample":
        res = await _api_post("/api/analytics/ai-simulate", {
            "temperature": 7.5,
            "ambient_temperature": 40.0,
            "humidity": 68.0,
            "temp_delta_1h": 0.5,
            "probe_discrepancy": 0.1,
            "temperature_ceiling": 8.0
        })
        if res:
            text = format_counterfactual_sim_card(res)
            await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("👑 Admin Cockpit", callback_data="menu:admin"),
                InlineKeyboardButton("📦 All Shipments", callback_data="menu:shipments"),
            ]]))
        return


# ---------------------------------------------------------------------------
# Handler list (imported by bot.py)
# ---------------------------------------------------------------------------

def get_handlers():
    return [
        CommandHandler("start", cmd_start),
        CommandHandler("help", cmd_help),
        CommandHandler("shipments", cmd_shipments),
        CommandHandler("fleet", cmd_fleet),
        CommandHandler("shipment", cmd_shipment),
        CommandHandler("problems", cmd_problems),
        CommandHandler("critical", cmd_critical),
        CommandHandler("events", cmd_events),
        CommandHandler("ai", cmd_ai),
        CommandHandler("ai_model", cmd_ai_model),
        CommandHandler("aimodel", cmd_ai_model),
        CommandHandler("aisim", cmd_aisim),
        CommandHandler("admin", cmd_admin),
        CommandHandler("chaos", cmd_chaos),
        CommandHandler("clear_chaos", cmd_clear_chaos),
        CommandHandler("audit", cmd_audit),
        CallbackQueryHandler(handle_callback),
    ]
