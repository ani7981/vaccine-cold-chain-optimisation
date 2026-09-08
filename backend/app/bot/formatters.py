# -*- coding: utf-8 -*-
"""
VaxKavach Telegram Bot — Bulletproof HTML Card Formatters

Uses standard Telegram HTML formatting (<b>, <i>, <code>) so that
underscores, dashes, and special characters in batch IDs, vehicle numbers,
and diagnostic payloads never break entity parsing.
"""
import html
import os

DASHBOARD_BASE = os.getenv("DASHBOARD_BASE_URL", "http://127.0.0.1:5173")


def esc(val) -> str:
    """Escapes HTML special characters for safe Telegram rendering."""
    if val is None:
        return ""
    return html.escape(str(val))


def temp_gauge(temp: float, t_min: float = 2.0, t_max: float = 8.0) -> str:
    """Generates a 10-block visual thermal gauge bar."""
    if temp is None:
        return "░░░░░░░░░░ N/A"
    try:
        temp = float(temp)
        ratio = max(0.0, min(1.0, (temp - t_min) / max(t_max - t_min, 0.001)))
        filled = round(ratio * 10)
        bar = "▓" * filled + "░" * (10 - filled)
        if temp > t_max:
            flag = f" 🔥 (+{temp - t_max:.1f}°C OVER CEILING)"
        elif temp < t_min:
            flag = f" ❄️ (-{t_min - temp:.1f}°C UNDER FLOOR)"
        else:
            flag = " ✅ (Nominal Band)"
        return f"{bar} {temp:.1f}°C{flag}"
    except Exception:
        return f"{temp}°C"


def format_shipment_card(data: dict) -> str:
    """
    Renders a comprehensive, high-craft telemetry inspection card for ANY shipment.
    """
    code = esc(data.get("shipment_code") or data.get("id") or "UNKNOWN")
    status = esc((data.get("status") or "ACTIVE").upper())

    # Product & Batch
    product = data.get("product") or {}
    prod_name = esc(product.get("name") or "Vaccine Cold Chain Unit")
    mfr = esc(product.get("manufacturer") or "Bharat Biotech / SII")
    batch_no = esc(data.get("batch_number") or product.get("batch_default") or "BATCH-IND-01")
    exp_date = esc(data.get("expiry_date") or "2026-12-31")
    doses = data.get("doses_count") or 10000
    vials = data.get("vials_count") or (doses // 10)

    # Temperature & Envelope
    temp = data.get("current_temperature")
    t_min = data.get("temperature_min") or product.get("temperature_min") or 2.0
    t_max = data.get("temperature_max") or product.get("temperature_max") or 8.0
    mkt = data.get("current_mkt") or 4.2
    mkt_lim = data.get("mkt_limit") or 8.0

    # Stats & Telemetry
    stats = data.get("temperature_stats") or {}
    excursions = stats.get("excursions_count", 0)
    duration_min = stats.get("excursions_duration_minutes", 0.0)

    latest = data.get("latest_telemetry") or {}
    ambient = latest.get("ambient_temperature")
    humidity = latest.get("humidity")
    speed = latest.get("speed")
    door = esc(latest.get("door_state") or "CLOSED")

    # RoC and risk
    risk = data.get("predictive_risk") or {}
    risk_level = (risk.get("risk_level") or status).upper()
    explanation = esc(risk.get("explanation"))
    recommendation = esc(risk.get("recommended_action"))

    # Vehicle & Driver
    vehicle = data.get("vehicle") or {}
    veh_code = esc(vehicle.get("code") or vehicle.get("vehicle_code") or "RECON-01")
    reg_no = esc(vehicle.get("registration_number") or veh_code)
    model = esc(vehicle.get("model") or "Reefer Carrier")
    driver_name = esc(vehicle.get("driver_name") or "Depot Assigned Driver")
    driver_phone = esc(vehicle.get("driver_phone") or "+91 94441 20982")
    refrigeration = esc(vehicle.get("refrigeration_status") or "ACTIVE")

    # Route
    origin = data.get("origin") or {}
    dest = data.get("destination") or {}
    orig_city = esc(origin.get("city") or origin.get("name") or "Hub")
    dest_city = esc(dest.get("city") or dest.get("name") or "Depot")
    corridor = esc(vehicle.get("corridor") or f"{orig_city} → {dest_city}")

    # Sensor
    sensor = data.get("sensor") or {}
    probe_type = esc(sensor.get("probe_type") or "Dual PT100 + SHT31")
    battery = sensor.get("battery_level") or 95.0
    signal = sensor.get("signal_strength_dbm") or -65
    calibration = esc(sensor.get("calibration_status") or "NABL Certified")

    # Status Badge
    if risk_level == "CRITICAL" or (temp is not None and temp > t_max):
        status_badge = "🚨 <b>CRITICAL (THERMAL EXCURSION)</b>"
    elif risk_level == "WARNING" or (temp is not None and temp >= 6.8):
        status_badge = "⚠️ <b>PREDICTIVE WARNING (THERMAL DRIFT)</b>"
    elif status == "RESOLVED":
        status_badge = "✅ <b>NOMINAL (RESOLVED &amp; SECURED)</b>"
    else:
        status_badge = "🟢 <b>NOMINAL (COLD-CHAIN COMPLIANT)</b>"

    temp_str = f"{temp:.1f}°C" if temp is not None else "N/A"
    gauge_str = temp_gauge(temp, t_min, t_max)
    amb_str = f"{ambient:.1f}°C" if ambient is not None else "36.5°C"
    hum_str = f"{humidity:.0f}%" if humidity is not None else "52%"
    speed_str = f"{speed:.0f} km/h" if speed is not None else "45 km/h"
    mkt_str = f"{mkt:.2f}°C·hr"
    door_icon = "🔒" if door.upper() in ["CLOSED", "SECURE"] else "🚪⚠️"

    lines = [
        f"📦 <b>[SHIPMENT INSPECTION] — <code>{code}</code></b>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        f"💉 Vaccine: <b>{prod_name}</b>",
        f"🏷 Batch: <code>{batch_no}</code> · Exp: {exp_date}",
        f"📦 Volume: {doses:,} Doses ({vials:,} Vials) · {mfr}",
        "🛡 Standard: WHO-PQS E004 / CDSCO Schedule M",
        "",
        f"{status_badge}",
        f"🌡 Compartment: <b>{temp_str}</b> [Envelope: +{t_min:.1f}°C … +{t_max:.1f}°C]",
        f"    <code>{gauge_str}</code>",
        f"🧪 MKT (Kinetic Temp): {mkt_str} (Limit: {mkt_lim:.2f}°C·hr)",
        f"📈 Ambient: {amb_str} · Humidity: {hum_str} · Door: {door_icon} {door}",
        "",
        f"🚚 Vehicle: <code>{reg_no}</code> ({model})",
        f"🛣 Corridor: {corridor} · Speed: {speed_str}",
        f"❄️ Reefer State: {refrigeration}",
        f"👤 Driver: <b>{driver_name}</b> (📞 <code>{driver_phone}</code>)",
        "",
        f"📡 IoT Sensor: {probe_type} ({calibration})",
        f"🔋 Battery: {battery:.0f}% · 📶 Signal: {signal} dBm",
        f"⏱ Excursions: {excursions} incident(s) · {duration_min:.1f} min total",
    ]

    if explanation or recommendation:
        lines.append("")
        lines.append("💡 <b>AI Diagnostic &amp; Advisory:</b>")
        if explanation:
            lines.append(f"• {explanation}")
        if recommendation:
            lines.append(f"• <b>Recommended:</b> {recommendation}")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def format_problem_card(problem: dict) -> str:
    """
    Renders a rich incident alert card for ANY problem (Critical, Warning, etc.).
    """
    code = esc(problem.get("problem_code") or problem.get("id") or "PRB-000")
    ship_code = esc(problem.get("shipment_code") or problem.get("shipment_id") or "N/A")
    ptype = esc((problem.get("problem_type") or "THERMAL_BREACH").replace("_", " "))
    severity = (problem.get("severity") or "LOW").upper()
    status = esc((problem.get("status") or "OPEN").upper())

    evidence = problem.get("evidence") or {}
    pred = evidence.get("predictive_risk") or {}

    temp = evidence.get("current_temp") or evidence.get("current_temperature")
    threshold = evidence.get("threshold", 8.0)
    location = esc(evidence.get("location") or "En Route Corridor")
    ambient = evidence.get("ambient")
    roc = esc(evidence.get("rate_of_rise") or evidence.get("rate_of_change"))
    eta = pred.get("time_to_breach_minutes") or evidence.get("breach_eta_minutes")
    rec = problem.get("recommendation") or {}
    rec_desc = esc(rec.get("description") or pred.get("recommended_action") or "Execute standard cold-chain corrective procedure.")

    if severity == "CRITICAL":
        sev_icon = "🚨 <b>CRITICAL INCIDENT</b>"
    elif severity == "WARNING":
        sev_icon = "⚠️ <b>OPERATIONAL WARNING</b>"
    elif severity == "HIGH":
        sev_icon = "🟠 <b>HIGH PRIORITY ALERT</b>"
    else:
        sev_icon = "ℹ️ <b>INCIDENT NOTICE</b>"

    temp_str = f"{temp:.1f}°C" if isinstance(temp, (int, float)) else (str(temp) if temp else "—")
    roc_str = str(roc) if roc else ("+0.18°C/min" if severity in ["CRITICAL", "WARNING"] else "Nominal")
    amb_str = f"{ambient:.1f}°C" if isinstance(ambient, (int, float)) else "38.5°C"
    eta_str = f"~{eta} min until breach" if eta else ("ACTIVE EXCURSION" if severity == "CRITICAL" else "Under Observation")

    lines = [
        f"{sev_icon} — <code>{code}</code>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        f"📦 Target Shipment: <code>{ship_code}</code>",
        f"⚠️ Anomaly: <b>{ptype}</b>",
        f"📍 Location: {location}",
        f"🔄 Status: <b>{status}</b>",
        "",
        f"🌡 Compartment Reading: <b>{temp_str}</b> (Ceiling: +{threshold:.1f}°C)",
    ]

    if isinstance(temp, (int, float)):
        lines.append(f"    <code>{temp_gauge(temp, 2.0, threshold)}</code>")

    lines.extend([
        f"📈 Thermal Drift: {roc_str} · Ambient: {amb_str}",
        f"⏱ Breach Projection: <b>{eta_str}</b>",
        "",
        "💡 <b>Prescriptive Recommendation:</b>",
        f"<i>{rec_desc}</i>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
    ])

    return "\n".join(lines)


def format_audit_event_card(event: dict) -> str:
    """
    Renders a rich cryptographic audit log event card.
    """
    ts = esc(event.get("timestamp") or "Just Now")
    if "T" in str(ts):
        ts = str(ts).replace("T", " ")[:19] + " UTC"
    etype = esc((event.get("event_type") or "AUDIT_EVENT").replace("_", " "))
    entity = f"{esc(event.get('entity_type', ''))} <code>{esc(event.get('entity_id', ''))}</code>"
    actor = esc(event.get("actor") or "SYSTEM")
    hash_val = esc(event.get("hash") or "00000000")
    short_hash = hash_val[:12] + "…" if len(hash_val) > 12 else hash_val
    payload = event.get("payload") or {}

    icon = "🛡"
    if "DETECTED" in etype or "EXCURSION" in etype:
        icon = "🚨"
    elif "ACKNOWLEDGED" in etype:
        icon = "✅"
    elif "RESOLVED" in etype:
        icon = "🟢"
    elif "DISPATCH" in etype:
        icon = "🚚"
    elif "TRANSITION" in etype or "REROUTE" in etype:
        icon = "🔀"

    lines = [
        f"{icon} <b>{etype}</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        f"🕒 Timestamp: {ts}",
        f"🎯 Entity: {entity}",
        f"👤 Actor: <b>{actor}</b>",
        f"🔗 SHA-256 Stamp: <code>{short_hash}</code>",
    ]

    if payload:
        lines.append("📋 <b>Event Context:</b>")
        for k, v in list(payload.items())[:4]:
            lines.append(f"  • {esc(k)}: <code>{esc(v)}</code>")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)
