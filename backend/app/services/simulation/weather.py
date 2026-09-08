import math
import random
from datetime import datetime, timezone
from typing import Dict, Any, Optional

CORRIDOR_MICROCLIMATES: Dict[str, Dict[str, Any]] = {
    "NH-48": {
        "region_name": "Tamil Nadu Coastal Plains & Palar Basin",
        "mean_ambient_c": 34.0,
        "diurnal_amplitude_c": 5.0,
        "base_humidity": 76.0,
        "peak_solar_w_m2": 880.0,
        "elevation_m": 80.0
    },
    "NH-44": {
        "region_name": "Deccan Semi-Arid Plateau (Rayalaseema / Telangana)",
        "mean_ambient_c": 36.5,
        "diurnal_amplitude_c": 7.0,
        "base_humidity": 44.0,
        "peak_solar_w_m2": 940.0,
        "elevation_m": 580.0
    },
    "NH-19": {
        "region_name": "Gangetic Northern Arterial (Indo-Gangetic Basin)",
        "mean_ambient_c": 39.0,
        "diurnal_amplitude_c": 8.0,
        "base_humidity": 48.0,
        "peak_solar_w_m2": 960.0,
        "elevation_m": 160.0
    },
    "NH-48-WEST": {
        "region_name": "Western Ghats Escarpment & Deccan Margin",
        "mean_ambient_c": 31.5,
        "diurnal_amplitude_c": 5.5,
        "base_humidity": 84.0,
        "peak_solar_w_m2": 820.0,
        "elevation_m": 620.0
    },
    "NH-106": {
        "region_name": "Brahmaputra Valley & Meghalaya Foothills",
        "mean_ambient_c": 27.5,
        "diurnal_amplitude_c": 4.5,
        "base_humidity": 88.0,
        "peak_solar_w_m2": 750.0,
        "elevation_m": 120.0
    }
}

class EnvironmentalWeatherEngine:
    """
    Stochastic Environmental Weather Engine:
    Computes spatially-varying, time-dependent atmospheric conditions:
    - Diurnal thermal cycles with localized peak insolation hours
    - Solar radiation flux (W/m^2) incident on highway vehicle bodies
    - Corridor-specific microclimatic humidity and elevation lapse rates
    - Stochastic Gaussian atmospheric micro-turbulence
    """

    def __init__(self):
        self.lapse_rate_per_100m = 0.65  # Standard atmospheric dry adiabatic lapse rate (°C / 100m)

    def get_weather(
        self,
        corridor: str,
        lat: float,
        lon: float,
        timestamp: Optional[datetime] = None,
        chaos_heatwave: bool = False
    ) -> Dict[str, Any]:
        """
        Computes accurate atmospheric telemetry at (lat, lon) along the specified corridor.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        climate = CORRIDOR_MICROCLIMATES.get(corridor.upper(), CORRIDOR_MICROCLIMATES["NH-48"])

        # Hour of day in Indian Standard Time (UTC + 5.5 hours)
        utc_hour = timestamp.hour + (timestamp.minute / 60.0) + (timestamp.second / 3600.0)
        ist_hour = (utc_hour + 5.5) % 24.0

        # Diurnal temperature cycle: peaks at 14:00 (2 PM), lowest at 05:00 (5 AM)
        # Shift phase so sine peak aligns with 14.0
        phase = (ist_hour - 8.0) * (2.0 * math.pi / 24.0)
        diurnal_offset = climate["diurnal_amplitude_c"] * math.sin(phase)

        # Solar radiation model: active between 06:00 and 18:00 IST
        if 6.0 <= ist_hour <= 18.0:
            solar_phase = (ist_hour - 6.0) * (math.pi / 12.0)
            solar_flux = climate["peak_solar_w_m2"] * math.sin(solar_phase)
        else:
            solar_flux = 0.0

        # Elevation lapse correction
        elevation = climate.get("elevation_m", 100.0)
        elevation_correction = -(elevation / 100.0) * self.lapse_rate_per_100m

        # Stochastic atmospheric noise (wind gusts, cloud shadows)
        noise = random.gauss(0.0, 0.25)

        ambient_temp = climate["mean_ambient_c"] + diurnal_offset + elevation_correction + noise

        # Humidity inverse relationship with daytime temperature
        humidity_offset = -(diurnal_offset * 1.8)
        humidity = max(20.0, min(98.0, climate["base_humidity"] + humidity_offset + random.gauss(0.0, 1.2)))

        # Heatwave Chaos Scenario Override
        if chaos_heatwave:
            ambient_temp += 8.5
            solar_flux = max(solar_flux, 1020.0)
            humidity = max(15.0, humidity - 15.0)

        return {
            "corridor": corridor,
            "region": climate["region_name"],
            "ambient_temperature_c": round(ambient_temp, 2),
            "solar_flux_w_m2": round(solar_flux, 1),
            "humidity_percent": round(humidity, 1),
            "ist_hour": round(ist_hour, 2),
            "elevation_m": elevation,
            "heatwave_active": chaos_heatwave
        }
