from datetime import datetime
from typing import Dict, Any

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
    transit_delay_active: bool
) -> Dict[str, Any]:
    
    evidence = {
        "temperature_limit": "NORMAL",
        "rate_of_change": roc_status,
        "door_event": "PRESENT" if door_state == "OPEN" else "ABSENT",
        "vehicle_idle": "PRESENT" if speed < 5.0 else "ABSENT",
        "ambient_heat": "HIGH" if ambient_temp > 35.0 else "NORMAL",
        "transit_delay": "ACTIVE" if transit_delay_active else "INACTIVE",
        "refrigeration": "DEGRADING" if refrigeration_state == "DEGRADED" else "NORMAL"
    }
    
    if current_temp > temp_max or mkt > mkt_limit:
        evidence["temperature_limit"] = "BREACHED"
        
    severity = "LOW"
    problem_type = "NONE"
    
    score = 0
    if evidence["temperature_limit"] == "BREACHED":
        score += 3
        problem_type = "temperature_problem"
    if evidence["rate_of_change"] == "CRITICAL":
        score += 3
    elif evidence["rate_of_change"] == "WARNING":
        score += 1
        
    if evidence["door_event"] == "PRESENT":
        score += 2
        if problem_type == "NONE":
            problem_type = "door_event"
            
    if evidence["refrigeration"] == "DEGRADING":
        score += 2
        problem_type = "refrigeration_problem"
        
    if evidence["transit_delay"] == "ACTIVE":
        score += 1
        
    if evidence["ambient_heat"] == "HIGH":
        score += 1
        
    if score >= 6:
        severity = "CRITICAL"
    elif score >= 4:
        severity = "HIGH"
    elif score >= 2:
        severity = "MEDIUM"
    elif score > 0:
        severity = "LOW"
    else:
        severity = "NONE"
        
    return {
        "has_problem": severity != "NONE",
        "severity": severity,
        "problem_type": problem_type if problem_type != "NONE" else "system_warning",
        "evidence": evidence
    }
