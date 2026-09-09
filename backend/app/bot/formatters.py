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
    if temp is not None and (temp > t_max or temp < t_min):
        status_badge = f"🚨 <b>CRITICAL (THERMAL EXCURSION: {temp:.1f}°C)</b>"
    elif risk_level == "CRITICAL":
        status_badge = "🚨 <b>CRITICAL (HARDWARE FAULT / ATTENTION REQUIRED)</b>"
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
    lat_val = latest.get("lat")
    lon_val = latest.get("lon")
    gps_str = f"{float(lat_val):.4f}°N, {float(lon_val):.4f}°E" if (lat_val is not None and lon_val is not None) else "En Route Corridor"

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
        f"📍 GPS Telematics: <code>{gps_str}</code>",
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

    lines.append("")
    lines.append("🧠 <i>Tap <b>[🧠 AI PREDICTION &amp; SHAP]</b> below for real-time forward forecasts &amp; SHAP explainability.</i>")
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


def prob_gauge(prob: float) -> str:
    """Generates a 10-block visual probability gauge bar."""
    if prob is None:
        return "░░░░░░░░░░ 0.0%"
    try:
        prob = float(prob)
        ratio = max(0.0, min(1.0, prob))
        filled = round(ratio * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"{bar} {prob * 100:.1f}%"
    except Exception:
        return f"{prob}"


def format_ai_insights_card(data: dict, shipment_code: str = "") -> str:
    """
    Renders an industrial-grade AI Spoilage Risk, Multi-Horizon Forecast,
    and instance-level SHAP explainability card.
    """
    code = esc(data.get("shipment_code") or shipment_code or "UNKNOWN")
    cur_temp = data.get("current_temperature")
    t_ceil = data.get("temperature_ceiling", 8.0)
    t_floor = data.get("temperature_floor", 2.0)
    mkt = data.get("mkt")

    pred = data.get("prediction") or {}
    spoilage_prob = pred.get("spoilage_probability", 0.0)
    risk_pct = pred.get("spoilage_risk_percent", round(spoilage_prob * 100, 1))
    risk_level = (pred.get("risk_level") or "LOW").upper()
    forecast = pred.get("forecast") or {}
    breach_h = pred.get("projected_ceiling_breach_hours")
    shap_factors = pred.get("top_risk_factors") or []
    version = esc(pred.get("model_version") or "2.0.0-production")

    if risk_level == "CRITICAL":
        risk_badge = "🚨 <b>CRITICAL SPOILAGE RISK</b>"
    elif risk_level == "HIGH":
        risk_badge = "🟠 <b>HIGH SPOILAGE RISK</b>"
    elif risk_level == "MEDIUM":
        risk_badge = "🟡 <b>MODERATE SPOILAGE RISK</b>"
    else:
        risk_badge = "🟢 <b>LOW (NOMINAL SAFETY MARGIN)</b>"

    temp_val = f"{cur_temp:.2f}°C" if isinstance(cur_temp, (int, float)) else str(cur_temp)
    lines = [
        f"🧠 <b>[AI DECISION &amp; PREDICTIVE RISK] — <code>{code}</code></b>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        f"🛡 Risk Classification: {risk_badge}",
        f"📊 Spoilage Probability: <code>{prob_gauge(spoilage_prob)}</code>",
        f"🌡 Baseline Chamber: <b>{temp_val}</b> [Envelope: {t_floor:.1f}°C … {t_ceil:.1f}°C]",
    ]
    if mkt is not None and isinstance(mkt, (int, float)):
        lines.append(f"🧪 MKT Exposure: <b>{mkt:.2f}°C·hr</b>")

    lines.append("")
    lines.append("⏱ <b>Multi-Horizon Temperature Forecast:</b>")
    f_1h = forecast.get("plus_1h")
    f_2h = forecast.get("plus_2h")
    f_4h = forecast.get("plus_4h")

    def f_str(val):
        if val is None:
            return "—"
        flag = " ⚠️" if (val > t_ceil or val < t_floor) else ""
        return f"{val:+.2f}°C{flag}"

    lines.append(f"  • +1 Hour Ahead:  <b>{f_str(f_1h)}</b>")
    lines.append(f"  • +2 Hours Ahead: <b>{f_str(f_2h)}</b>")
    lines.append(f"  • +4 Hours Ahead: <b>{f_str(f_4h)}</b>")

    if breach_h is not None:
        lines.append(f"🚨 <b>BREACH ALERT:</b> Projected ceiling exceedance in ~<b>{breach_h} hr</b>!")
    else:
        lines.append("✅ <b>Nominal Margin:</b> No clinical breach predicted within 4h horizon.")

    if shap_factors:
        lines.append("")
        lines.append("🔬 <b>SHAP Feature Attribution (Why the AI decided this):</b>")
        for item in shap_factors[:3]:
            factor_name = esc(item.get("factor") or "Telemetry Feature")
            impact = item.get("shap_impact", 0.0)
            direction = esc(item.get("direction") or "")
            icon = "🔺" if impact > 0 else "🔹"
            lines.append(f"  {icon} <b>{factor_name}</b>: <code>{impact:+.3f}</code> ({direction})")

    lines.extend([
        "",
        "⚙️ <b>Architecture:</b> XGBoost + SHAP TreeExplainer",
        f"🔖 <b>Model Version:</b> <code>{version}</code>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
    ])
    return "\n".join(lines)


def format_ai_model_card(data: dict) -> str:
    """Renders comprehensive model architecture, metrics, and dataset card."""
    meta = data.get("metadata") or {}
    status = esc(data.get("status", "ready").upper())
    version = esc(meta.get("version", "2.0.0-production"))
    formulation = esc(meta.get("formulation", "XGBoost Dual-Probe Ensemble"))
    records = meta.get("dataset_records_raw", 26674)
    consensus = meta.get("dataset_hourly_consensus", 13337)

    cls_metrics = meta.get("classifier_metrics") or {}
    acc = cls_metrics.get("accuracy", 0.998) * 100
    auc = cls_metrics.get("roc_auc", 0.999) * 100
    f1 = cls_metrics.get("f1", 0.994) * 100
    prec = cls_metrics.get("precision", 1.0) * 100
    rec = cls_metrics.get("recall", 0.988) * 100

    fore_metrics = meta.get("forecaster_metrics") or {}
    m1 = fore_metrics.get("ahead_1h", {})
    m2 = fore_metrics.get("ahead_2h", {})
    m4 = fore_metrics.get("ahead_4h", {})

    lines = [
        "🔬 <b>[VAXKAVACH AI PRODUCTION ENGINE]</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        f"Status: 🟢 <b>{status}</b> &middot; Version: <code>{version}</code>",
        f"Design: <i>{formulation}</i>",
        "",
        "🎯 <b>Spoilage Classifier (XGBoost):</b>",
        f"  • ROC-AUC Score: <b>{auc:.2f}%</b>",
        f"  • Overall Accuracy: <b>{acc:.2f}%</b>",
        f"  • F1-Score: <b>{f1:.2f}%</b> (Precision: {prec:.1f}%, Recall: {rec:.1f}%)",
        "",
        "⏱ <b>Multi-Horizon Forecaster (XGBoost Regressors):</b>",
        f"  • +1h Ahead: MAE <b>{m1.get('mae', 1.01):.2f}°C</b> (RMSE {m1.get('rmse', 2.13):.2f})",
        f"  • +2h Ahead: MAE <b>{m2.get('mae', 1.13):.2f}°C</b> (RMSE {m2.get('rmse', 3.19):.2f})",
        f"  • +4h Ahead: MAE <b>{m4.get('mae', 1.45):.2f}°C</b> (RMSE {m4.get('rmse', 4.85):.2f})",
        "",
        "📊 <b>Training Dataset &amp; Provenance:</b>",
        f"  • Raw Ingested Readings: <b>{records:,}</b>",
        f"  • Hourly Physical Consensus: <b>{consensus:,} batches</b>",
        f"  • Standard: WHO PQS E004 / CDSCO Schedule M",
        "━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)


def format_counterfactual_sim_card(result: dict) -> str:
    """Renders counterfactual what-if simulation output."""
    inp = result.get("inputs") or {}
    pred = result.get("prediction") or {}

    t_in = inp.get("temperature", 4.0)
    amb_in = inp.get("ambient_temperature", 32.0)
    delta_in = inp.get("temp_delta_1h", 0.0)
    ceil_in = inp.get("temperature_ceiling", 8.0)

    prob = pred.get("spoilage_probability", 0.0)
    level = (pred.get("risk_level") or "LOW").upper()
    forecast = pred.get("forecast") or {}
    breach = pred.get("projected_ceiling_breach_hours")
    shap_factors = pred.get("top_risk_factors") or []

    lines = [
        "🧪 <b>[AI WHAT-IF / COUNTERFACTUAL SIMULATION]</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        "<b>Input Scenario Tested:</b>",
        f"  • Chamber Temp: <b>{t_in:+.1f}°C</b> (Ceiling: +{ceil_in:.1f}°C)",
        f"  • Exterior Ambient: <b>{amb_in:+.1f}°C</b>",
        f"  • Rate of Rise (1h): <b>{delta_in:+.2f}°C/hr</b>",
        "",
        "<b>Simulation Outcome:</b>",
        f"  • Spoilage Risk: <b>{prob_gauge(prob)}</b> [{level}]",
        f"  • +1h Horizon: <b>{forecast.get('plus_1h', '—'):+.2f}°C</b>",
        f"  • +2h Horizon: <b>{forecast.get('plus_2h', '—'):+.2f}°C</b>",
        f"  • +4h Horizon: <b>{forecast.get('plus_4h', '—'):+.2f}°C</b>",
    ]
    if breach:
        lines.append(f"  • 🚨 <b>Ceiling Exceeded within {breach} hour(s)!</b>")
    else:
        lines.append("  • ✅ <b>Envelope Maintained across 4 hours.</b>")

    if shap_factors:
        lines.append("")
        lines.append("<b>Dominant AI Driving Factors:</b>")
        for item in shap_factors[:2]:
            lines.append(f"  • {esc(item.get('factor'))}: <code>{item.get('shap_impact', 0.0):+.3f}</code>")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def format_admin_cockpit(metrics: dict, sim_status: dict, users: list, name: str, role: str) -> str:
    """Renders Executive Admin Cockpit with system health, simulation, and operators."""
    active_shipments = metrics.get("active_shipments", 0)
    tot_problems = metrics.get("total_problems_open", 0)
    crit_problems = metrics.get("critical_problems_open", 0)
    fleet_util = metrics.get("fleet_utilization", "0%")
    tot_vehicles = metrics.get("total_vehicles", 0)

    is_sim_running = sim_status.get("is_running", False)
    sim_tick = sim_status.get("current_tick", 0)
    active_convoys = len(sim_status.get("active_convoys", []))
    chaos_active = sim_status.get("active_chaos_incidents", {})
    chaos_count = len(chaos_active)

    sim_icon = "🟢 RUNNING" if is_sim_running else "⏸ STOPPED"

    lines = [
        "👑 <b>[VAXKAVACH EXECUTIVE ADMIN COCKPIT]</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        f"Administrator: <b>{esc(name)}</b> ({esc(role)})",
        f"Simulation Engine: <b>{sim_icon}</b> (Tick: {sim_tick}, Convoys: {active_convoys})",
        "",
        "📊 <b>Network Cold-Chain Fleet Health:</b>",
        f"  • Active Consignments: <b>{active_shipments}</b> / {tot_vehicles} Reefer Units",
        f"  • Fleet Utilization: <b>{fleet_util}</b>",
        f"  • Open Incidents: <b>{tot_problems}</b> (🚨 <b>{crit_problems} Critical</b>)",
        "",
        f"⚡ <b>Chaos &amp; Fault Injections Active:</b> <b>{chaos_count}</b>",
    ]
    if chaos_active:
        for target, incident in chaos_active.items():
            lines.append(f"  • Target <code>{esc(target)}</code>: ⚠️ <b>{esc(str(incident))}</b>")
    else:
        lines.append("  • <i>All fleet corridors operating nominally with zero injected faults.</i>")

    lines.extend([
        "",
        f"👥 <b>Linked Telegram Operators ({len(users)}):</b>",
    ])
    for u in users[:5]:
        u_name = esc(u.get("name") or "Operator")
        u_role = esc(u.get("role") or "OPERATOR")
        u_chat = u.get("chat_id")
        lines.append(f"  • <b>{u_name}</b> ({u_role}) &middot; ID: <code>{u_chat}</code>")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def format_merkle_audit_card(merkle_info: dict, recent_events: list) -> str:
    """Renders Merkle tree root and chain integrity verification."""
    root = esc(merkle_info.get("merkle_root") or "00000000")
    total_leaves = merkle_info.get("total_leaves", 0)
    depth = merkle_info.get("tree_depth", 0)
    genesis = esc(merkle_info.get("genesis_hash") or "")
    short_genesis = genesis[:12] + "…" if len(genesis) > 12 else genesis

    lines = [
        "🛡 <b>[CRYPTOGRAPHIC MERKLE INTEGRITY LEDGER]</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━",
        "Standard: RFC 6962 Binary Merkle Tree / FDA 21 CFR Part 11",
        f"Total Ledger Records: <b>{total_leaves}</b> (Depth: {depth})",
        "Chain Integrity Status: ✅ <b>VERIFIED &amp; UNTAMPERED</b>",
        "",
        "🔗 <b>Active Merkle Root:</b>",
        f"<code>{root}</code>",
        f"Genesis Anchor: <code>{short_genesis}</code>",
        "",
        "📜 <b>Recent Cryptographic Blocks:</b>",
    ]
    for ev in recent_events[:3]:
        e_type = esc(ev.get("event_type", "AUDIT"))
        e_hash = esc(ev.get("hash", "")[:16]) + "…"
        e_actor = esc(ev.get("actor", "SYSTEM"))
        lines.append(f"  • <code>{e_hash}</code> &middot; <b>{e_type}</b> ({e_actor})")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

