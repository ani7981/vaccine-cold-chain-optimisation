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
            InlineKeyboardButton(
                "🌐 OPEN DASHBOARD",
                url=f"{DASHBOARD_BASE}/shipment.html?id={shipment_code}"
            ),
        ])
    else:
        rows.append([
            InlineKeyboardButton(
                "🌐 OPEN DASHBOARD",
                url=f"{DASHBOARD_BASE}/shipment.html?id={shipment_code}"
            ),
            InlineKeyboardButton("🔄 REFRESH", callback_data=f"shipment:{shipment_code}"),
        ])

    rows.append([
        InlineKeyboardButton("📦 ALL SHIPMENTS", callback_data="menu:shipments"),
        InlineKeyboardButton("⚠️ ACTIVE PROBLEMS", callback_data="menu:problems"),
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
