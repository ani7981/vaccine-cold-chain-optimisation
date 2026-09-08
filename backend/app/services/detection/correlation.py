from typing import Dict, Any, Optional
from app.services.ai import ai_service

def evaluate_signals(
    current_temp: float, 
    mkt: float, 
    mkt_limit: float, 
    temp_max: float, 
    roc_status: str,
    door_state: str,
    speed: float,
    ambient_temp: float,
    refrigeration_state: str,
    transit_delay_active: bool,
    extra_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Hierarchical 4-Tier Cold-Chain Decision Architecture:
    1. Tier 1: Deterministic WHO-PQS Clinical Guardrails (hard temperature & MKT envelope)
    2. Tier 2: Thermal Kinetics (Arrhenius Mean Kinetic Temperature exposure)
    3. Tier 3: Predictive Machine Learning (XGBoost 4h lookahead risk, multi-horizon forecaster, TreeExplainer SHAP)
    4. Tier 4: Prescriptive Operational Mitigation Actions
    """
    context = extra_context or {}
    temp_min = float(context.get("temp_min", 2.0))
    
    # ----------------------------------------------------
    # TIER 1: DETERMINISTIC WHO-PQS CLINICAL GUARDRAILS
    # ----------------------------------------------------
    evidence = {
        "temperature_limit": "NORMAL",
        "rate_of_change": roc_status,
        "door_event": "PRESENT" if door_state == "OPEN" else "ABSENT",
        "vehicle_idle": "PRESENT" if speed < 5.0 else "ABSENT",
        "ambient_heat": "HIGH" if ambient_temp > 35.0 else "NORMAL",
        "transit_delay": "ACTIVE" if transit_delay_active else "INACTIVE",
        "refrigeration": "DEGRADING" if refrigeration_state in ["DEGRADED", "FAULT"] else "NORMAL"
    }
    
    is_temp_breached = current_temp > temp_max or current_temp < temp_min
    is_mkt_breached = mkt > mkt_limit
    
    if is_temp_breached or is_mkt_breached:
        evidence["temperature_limit"] = "BREACHED"
        
    # ----------------------------------------------------
    # TIER 2 & 3: AI PREDICTIVE RISK & MULTI-HORIZON FORECAST
    # ----------------------------------------------------
    ai_features = {
        "temperature": current_temp,
        "probe_1_temp": float(context.get("probe_1_temp", current_temp)),
        "probe_2_temp": float(context.get("probe_2_temp", current_temp)),
        "probe_discrepancy": float(context.get("probe_discrepancy", 0.1)),
        "ambient_temperature": ambient_temp,
        "humidity": float(context.get("humidity", 65.0)),
        "temp_delta_1h": float(context.get("temp_delta_1h", 0.0)),
        "temp_delta_3h": float(context.get("temp_delta_3h", 0.0)),
        "temp_accel": float(context.get("temp_accel", 0.0)),
        "temp_rolling_mean_3h": float(context.get("temp_rolling_mean_3h", current_temp)),
        "temp_rolling_std_3h": float(context.get("temp_rolling_std_3h", 0.1)),
        "hours_in_transit": float(context.get("hours_in_transit", 12.0))
    }
    
    ai_result = ai_service.predict(ai_features, temp_ceiling=temp_max, temp_floor=temp_min)
    spoilage_prob = ai_result.get("spoilage_probability", 0.0)
    projected_breach_hrs = ai_result.get("projected_ceiling_breach_hours")
    
    # ----------------------------------------------------
    # TIER 4: HIERARCHICAL SYNTHESIS & OPERATIONAL MITIGATION
    # ----------------------------------------------------
    problem_type = "NONE"
    severity = "NONE"
    recommended_action = "Maintain standard nominal routing and monitoring."
    
    if is_temp_breached or is_mkt_breached:
        # Guardrail hard breach takes unconditional precedence
        problem_type = "temperature_problem"
        severity = "CRITICAL" if current_temp >= (temp_max + 1.0) or spoilage_prob >= 0.70 else "HIGH"
        recommended_action = "IMMEDIATE EMERGENCY: Reroute shipment to nearest certified cold storage depot. Verify refrigeration unit power and replenish coolant."
    elif evidence["refrigeration"] == "DEGRADING":
        problem_type = "refrigeration_problem"
        severity = "HIGH" if ambient_temp > 38.0 or spoilage_prob >= 0.50 else "MEDIUM"
        recommended_action = "Refrigeration degradation detected. Transfer active payload to passive backup compartment and notify depot dispatch."
    elif evidence["door_event"] == "PRESENT":
        problem_type = "door_event"
        severity = "HIGH" if ambient_temp > 35.0 else "MEDIUM"
        recommended_action = "Container door open under adverse ambient conditions. Command driver to verify seal closure immediately."
    elif roc_status == "CRITICAL":
        problem_type = "temperature_problem"
        severity = "HIGH"
        recommended_action = "Rapid thermal rate-of-change detected. Check insulation barrier integrity."
    elif projected_breach_hrs is not None and projected_breach_hrs <= 2:
        # Proactive AI early intervention: container is currently safe but predicted to breach within 2 hours
        problem_type = "predictive_excursion"
        severity = "HIGH" if spoilage_prob >= 0.60 else "MEDIUM"
        recommended_action = f"PREDICTIVE INTERVENTION: Temperature breach projected within {projected_breach_hrs} hour(s). Expedite route or prep cold storage transfer."
    elif spoilage_prob >= 0.65:
        problem_type = "predictive_spoilage_risk"
        severity = "MEDIUM"
        recommended_action = "Machine learning indicates high spoilage risk trajectory. Monitor telemetry at heightened 1-minute sampling frequency."
    elif roc_status == "WARNING" or evidence["ambient_heat"] == "HIGH":
        problem_type = "system_warning"
        severity = "LOW"
        recommended_action = "Adverse ambient conditions observed. Ensure thermal shipper stays shaded and enclosed."
        
    has_problem = severity != "NONE" and severity != "LOW"
    
    return {
        "has_problem": has_problem,
        "severity": severity,
        "problem_type": problem_type if problem_type != "NONE" else "system_warning",
        "evidence": evidence,
        "recommended_action": recommended_action,
        "ai_insights": {
            "spoilage_probability": spoilage_prob,
            "spoilage_risk_percent": round(spoilage_prob * 100, 1),
            "ai_risk_level": ai_result.get("risk_level", "LOW"),
            "temperature_forecast": ai_result.get("forecast", {}),
            "projected_ceiling_breach_hours": projected_breach_hrs,
            "top_risk_factors": ai_result.get("top_risk_factors", []),
            "model_version": ai_result.get("model_version", "2.0.0-production")
        }
    }
