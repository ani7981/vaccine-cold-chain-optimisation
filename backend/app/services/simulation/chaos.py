import time
from typing import Dict, Any, List, Optional

class ChaosIncidentManager:
    """
    Chaos & Adversarial Incident Injector for Cold-Chain Stress Testing:
    Allows real-time injection of catastrophic and non-nominal conditions:
    - COMPRESSOR_FAILURE: Chiller abruptly loses power / coolant leak
    - HEATWAVE_SURGE: Microclimatic temperature spike (+10°C) and extreme solar flux
    - DOOR_AJAR: State border RTO/Toll inspection with compartment doors propped open
    - TRAFFIC_GRIDLOCK: Highway blockage drops speed to 0 km/h, causing engine heat soak
    - SENSOR_PROBE_DRIFT: Asymmetric sensor calibration drift exceeding 1.5°C
    """

    VALID_INCIDENTS = [
        "COMPRESSOR_FAILURE",
        "HEATWAVE_SURGE",
        "DOOR_AJAR",
        "TRAFFIC_GRIDLOCK",
        "SENSOR_PROBE_DRIFT",
        "NORMAL"
    ]

    def __init__(self):
        # Maps shipment_id -> Dict of active chaos attributes
        self._active_incidents: Dict[str, Dict[str, Any]] = {}

    def inject_incident(
        self,
        shipment_id: str,
        incident_type: str,
        duration_seconds: Optional[int] = 300,
        severity: str = "CRITICAL",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        inc_type = incident_type.upper()
        if inc_type not in self.VALID_INCIDENTS:
            raise ValueError(f"Unknown incident type '{incident_type}'. Valid: {self.VALID_INCIDENTS}")

        if inc_type == "NORMAL":
            self.clear_shipment(shipment_id)
            return {
                "status": "NORMALIZED",
                "shipment_id": shipment_id,
                "active_incidents": []
            }

        expiry_time = (time.time() + duration_seconds) if duration_seconds else None

        incident_record = {
            "type": inc_type,
            "severity": severity,
            "injected_at": time.time(),
            "expiry_time": expiry_time,
            "duration_seconds": duration_seconds,
            "metadata": metadata or {}
        }

        if shipment_id not in self._active_incidents:
            self._active_incidents[shipment_id] = {}

        self._active_incidents[shipment_id][inc_type] = incident_record

        return {
            "status": "INJECTED",
            "shipment_id": shipment_id,
            "incident": incident_record,
            "all_active": list(self._active_incidents[shipment_id].keys())
        }

    def get_shipment_overrides(self, shipment_id: str) -> Dict[str, Any]:
        """
        Returns active physical overrides for the shipment after pruning expired incidents.
        """
        now = time.time()
        overrides = {
            "chiller_state": "NORMAL",
            "door_state": "CLOSED",
            "speed_override": None,
            "heatwave_active": False,
            "probe_drift_delta": 0.0,
            "active_incident_types": []
        }

        if shipment_id not in self._active_incidents:
            return overrides

        active = self._active_incidents[shipment_id]
        expired = []

        for inc_type, data in list(active.items()):
            if data["expiry_time"] and now > data["expiry_time"]:
                expired.append(inc_type)
                continue

            overrides["active_incident_types"].append(inc_type)

            if inc_type == "COMPRESSOR_FAILURE":
                overrides["chiller_state"] = "FAILED"
            elif inc_type == "HEATWAVE_SURGE":
                overrides["heatwave_active"] = True
            elif inc_type == "DOOR_AJAR":
                overrides["door_state"] = "OPEN"
            elif inc_type == "TRAFFIC_GRIDLOCK":
                overrides["speed_override"] = 0.0
            elif inc_type == "SENSOR_PROBE_DRIFT":
                overrides["probe_drift_delta"] = 2.45

        for exp in expired:
            del active[exp]

        return overrides

    def clear_shipment(self, shipment_id: str):
        if shipment_id in self._active_incidents:
            del self._active_incidents[shipment_id]

    def clear_all(self):
        self._active_incidents.clear()

    def get_all_active(self) -> Dict[str, Any]:
        now = time.time()
        result = {}
        for s_id, incidents in self._active_incidents.items():
            valid = {
                k: v for k, v in incidents.items()
                if not v["expiry_time"] or now <= v["expiry_time"]
            }
            if valid:
                result[s_id] = list(valid.keys())
        return result

chaos_manager = ChaosIncidentManager()
