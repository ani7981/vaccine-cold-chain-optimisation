from typing import List, Tuple
from datetime import datetime

class RateOfChangeDetector:
    def __init__(self, warning_threshold: float, critical_threshold: float, sustained_duration_seconds: int):
        self.warning_threshold = warning_threshold  # °C/min
        self.critical_threshold = critical_threshold
        self.sustained_duration_seconds = sustained_duration_seconds

    def check(self, readings: List[dict]) -> str:
        """
        readings format: [{"timestamp": datetime, "temperature": float}]
        Returns "NORMAL", "WARNING", "CRITICAL"
        """
        if len(readings) < 2:
            return "NORMAL"
            
        readings = sorted(readings, key=lambda x: x["timestamp"])
        
        # Check overall rate from oldest to newest in the window
        oldest = readings[0]
        newest = readings[-1]
        
        time_diff = (newest["timestamp"] - oldest["timestamp"]).total_seconds()
        if time_diff < self.sustained_duration_seconds:
            return "NORMAL" # hasn't sustained long enough yet
            
        # calculate rate over the window
        minutes = time_diff / 60.0
        if minutes == 0:
            return "NORMAL"
            
        rate = (newest["temperature"] - oldest["temperature"]) / minutes
        
        if rate >= self.critical_threshold:
            return "CRITICAL"
        elif rate >= self.warning_threshold:
            return "WARNING"
            
        return "NORMAL"
