# -*- coding: utf-8 -*-
"""
VaxKavach Telegram Bot — Inline Keyboards
callback_data convention: ACTION:entity_id
"""
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

DASHBOARD_BASE = os.getenv("DASHBOARD_BASE_URL", "http://127.0.0.1:5173")


def critical_alert_keyboard(problem_id: str, shipment_code: str) -> InlineKeyboardMarkup:
    """Keyboard attached to a critical thermal-breach alert."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔀 DIVERT NOW", callback_data=f"divert:{problem_id}"),
            InlineKeyboardButton("✅ ACKNOWLEDGE", callback_data=f"ack:{problem_id}"),
        ],
        [
            InlineKeyboardButton("📣 ESCALATE", callback_data=f"escalate:{problem_id}"),
            InlineKeyboardButton(
                "🌐 OPEN DASHBOARD",
                url=f"{DASHBOARD_BASE}/shipment.html?id={shipment_code}"
            ),
        ],
    ])


def problem_action_keyboard(problem_id: str, shipment_code: str, severity: str = "WARNING") -> InlineKeyboardMarkup:
    """Keyboard for any active problem (Critical, Warning, etc.)."""
    buttons = []
    if severity.upper() in ["CRITICAL", "HIGH"]:
        buttons.append([
            InlineKeyboardButton("🔀 DIVERT NOW", callback_data=f"divert:{problem_id}"),
            InlineKeyboardButton("✅ ACKNOWLEDGE", callback_data=f"ack:{problem_id}"),
        ])
        buttons.append([
            InlineKeyboardButton("📣 ESCALATE", callback_data=f"escalate:{problem_id}"),
            InlineKeyboardButton("📦 INSPECT SHIPMENT", callback_data=f"shipment:{shipment_code}"),
        ])
    else:
        buttons.append([
            InlineKeyboardButton("✅ ACKNOWLEDGE", callback_data=f"ack:{problem_id}"),
            InlineKeyboardButton("📣 ESCALATE", callback_data=f"escalate:{problem_id}"),
        ])
        buttons.append([
            InlineKeyboardButton("📦 INSPECT SHIPMENT", callback_data=f"shipment:{shipment_code}"),
            InlineKeyboardButton(
                "🌐 DASHBOARD",
                url=f"{DASHBOARD_BASE}/shipment.html?id={shipment_code}"
            ),
        ])
    return InlineKeyboardMarkup(buttons)


def shipment_detail_keyboard(shipment_code: str, problem_id: str = None, status: str = "ACTIVE") -> InlineKeyboardMarkup:
    """Keyboard for a single detailed shipment card."""
    rows = []
    if problem_id:
        rows.append([
            InlineKeyboardButton("🔀 DIVERT NOW", callback_data=f"divert:{problem_id}"),
            InlineKeyboardButton("✅ ACKNOWLEDGE", callback_data=f"ack:{problem_id}"),
        ])
        rows.append([
            InlineKeyboardButton("📣 ESCALATE", callback_data=f"escalate:{problem_id}"),
            InlineKeyboardButton("🧠 AI INSIGHTS", callback_data=f"ai:{shipment_code}"),
        ])
    else:
        rows.append([
            InlineKeyboardButton("🧠 AI PREDICTION & SHAP", callback_data=f"ai:{shipment_code}"),
            InlineKeyboardButton("⚡ CHAOS TEST", callback_data=f"chaos_select:{shipment_code}"),
        ])
        rows.append([
            InlineKeyboardButton("🔄 REFRESH", callback_data=f"shipment:{shipment_code}"),
            InlineKeyboardButton(
                "🌐 DASHBOARD",
                url=f"{DASHBOARD_BASE}/shipment.html?id={shipment_code}"
            ),
        ])

    rows.append([
        InlineKeyboardButton("📦 ALL SHIPMENTS", callback_data="menu:shipments"),
        InlineKeyboardButton("⚠️ PROBLEMS", callback_data="menu:problems"),
        InlineKeyboardButton("👑 ADMIN COCKPIT", callback_data="menu:admin"),
    ])
    return InlineKeyboardMarkup(rows)


def shipments_selector_keyboard(shipments: list) -> InlineKeyboardMarkup:
    """
    Creates an interactive 2-column grid of buttons for all shipments.
    Tapping any button instantly displays its full rich telemetry card.
    """
    buttons = []
    row = []

    for s in shipments:
        code = s.get("shipment_code") or s.get("id") or "?"
        temp = s.get("current_temperature")
        prob = s.get("current_problem")

        # Status icon
        if prob and (prob.get("severity") == "CRITICAL" or (temp and temp > 8.0)):
            icon = "🔴"
        elif prob or (temp and (temp >= 6.8 or temp < 2.2)):
            icon = "🟡"
        else:
            icon = "🟢"

        temp_str = f"{temp:.1f}°" if temp is not None else ""
        label = f"{icon} {code} {temp_str}".strip()

        row.append(InlineKeyboardButton(label, callback_data=f"shipment:{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton("🚨 Critical Only", callback_data="menu:critical"),
        InlineKeyboardButton("⚠️ Problems", callback_data="menu:problems"),
        InlineKeyboardButton("🔄 Refresh", callback_data="menu:shipments"),
    ])
    return InlineKeyboardMarkup(buttons)


def confirm_divert_keyboard(problem_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ YES — Execute Divert", callback_data=f"divert_confirm:{problem_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"divert_cancel:{problem_id}"),
        ]
    ])


def confirm_escalate_keyboard(problem_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ YES — Escalate", callback_data=f"escalate_confirm:{problem_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"escalate_cancel:{problem_id}"),
        ]
    ])


def fleet_status_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 All Shipments Grid", callback_data="menu:shipments"),
            InlineKeyboardButton("⚠️ Active Problems", callback_data="menu:problems"),
        ],
        [
            InlineKeyboardButton("🚨 Critical Alerts", callback_data="menu:critical"),
            InlineKeyboardButton("📜 Event Log", callback_data="menu:events"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh Fleet", callback_data="menu:fleet"),
        ]
    ])


def problems_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚨 Critical Only", callback_data="menu:critical"),
            InlineKeyboardButton("📦 All Shipments", callback_data="menu:shipments"),
        ],
        [
            InlineKeyboardButton("📜 Event Log", callback_data="menu:events"),
            InlineKeyboardButton("🔄 Refresh Incidents", callback_data="menu:problems"),
        ]
    ])


def events_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚠️ Active Problems", callback_data="menu:problems"),
            InlineKeyboardButton("📦 All Shipments", callback_data="menu:shipments"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh Events", callback_data="menu:events"),
        ]
    ])


def ai_insight_keyboard(shipment_code: str) -> InlineKeyboardMarkup:
    """Keyboard for AI Deep-Dive Card."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 RE-RUN AI INFERENCE", callback_data=f"ai:{shipment_code}"),
            InlineKeyboardButton("🧪 WHAT-IF LAB", callback_data=f"aisim_launch:{shipment_code}"),
        ],
        [
            InlineKeyboardButton("⚡ INJECT CHAOS", callback_data=f"chaos_select:{shipment_code}"),
            InlineKeyboardButton("📦 SHIPMENT TELEMETRY", callback_data=f"shipment:{shipment_code}"),
        ],
        [
            InlineKeyboardButton("🔬 MODEL SPECS", callback_data="menu:ai_model"),
            InlineKeyboardButton(
                "🌐 WEB DASHBOARD",
                url=f"{DASHBOARD_BASE}/shipment.html?id={shipment_code}"
            ),
        ],
        [
            InlineKeyboardButton("👑 ADMIN COCKPIT", callback_data="menu:admin"),
            InlineKeyboardButton("📦 ALL SHIPMENTS", callback_data="menu:shipments"),
        ]
    ])


def admin_cockpit_keyboard() -> InlineKeyboardMarkup:
    """Executive Admin Master Control Grid."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔬 AI Model Specs", callback_data="menu:ai_model"),
            InlineKeyboardButton("⚡ Chaos Injector", callback_data="menu:chaos_hub"),
        ],
        [
            InlineKeyboardButton("🛡 Merkle Audit Ledger", callback_data="menu:audit"),
            InlineKeyboardButton("📦 Fleet Shipments", callback_data="menu:shipments"),
        ],
        [
            InlineKeyboardButton("⚠️ Active Problems", callback_data="menu:problems"),
            InlineKeyboardButton("🔄 Refresh Cockpit", callback_data="menu:admin"),
        ]
    ])


def chaos_selector_keyboard(shipment_code: str) -> InlineKeyboardMarkup:
    """Keyboard for injecting synthetic chaos anomalies."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 Compressor Drop", callback_data=f"chaos_do:{shipment_code}:COMPRESSOR_FAILURE"),
            InlineKeyboardButton("☀️ Heatwave Surge", callback_data=f"chaos_do:{shipment_code}:HEATWAVE_SURGE"),
        ],
        [
            InlineKeyboardButton("🚪 Door Breach", callback_data=f"chaos_do:{shipment_code}:DOOR_AJAR"),
            InlineKeyboardButton("📡 Sensor Drift", callback_data=f"chaos_do:{shipment_code}:SENSOR_PROBE_DRIFT"),
        ],
        [
            InlineKeyboardButton("🛑 Clear All Faults", callback_data=f"chaos_clear:{shipment_code}"),
            InlineKeyboardButton("🧠 AI Risk Card", callback_data=f"ai:{shipment_code}"),
        ],
        [
            InlineKeyboardButton("📦 Back to Shipment", callback_data=f"shipment:{shipment_code}"),
        ]
    ])


def audit_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for Merkle Audit Deck."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔒 Verify Merkle Tree", callback_data="audit:verify"),
            InlineKeyboardButton("📜 Recent Blocks", callback_data="menu:events"),
        ],
        [
            InlineKeyboardButton("👑 Admin Cockpit", callback_data="menu:admin"),
            InlineKeyboardButton("📦 All Shipments", callback_data="menu:shipments"),
        ]
    ])


def ai_model_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for AI Model Information."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🧪 What-If Simulation", callback_data="menu:aisim_sample"),
            InlineKeyboardButton("👑 Admin Cockpit", callback_data="menu:admin"),
        ],
        [
            InlineKeyboardButton("📦 Inspect Fleet", callback_data="menu:shipments"),
        ]
    ])

