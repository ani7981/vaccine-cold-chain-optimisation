import math
from typing import Dict, Any, Optional

class ReeferThermodynamicModel:
    """
    First-Principles Newton-Fourier Thermodynamic Reefer Model:
    Governs heat transfer through refrigerated transport containers:
      dQ_net = Q_conduction + Q_solar + Q_infiltration - Q_cooling
      dT/dt  = dQ_net / C_thermal

    Parameters reflect standard WHO-PQS certified pharmaceutical reefer vehicles
    (e.g., Tata Signa 2823 Reefer with Thermo King / Carrier Transicold chilling units).
    """

    def __init__(
        self,
        u_wall: float = 0.36,         # W / (m^2 * K) - Polyurethane foam insulation
        surface_area: float = 62.0,   # m^2 - Total surface area of 20ft container box
        roof_area: float = 14.5,      # m^2 - Projected horizontal roof area
        solar_absorptivity: float = 0.20, # Low absorptivity (reflective clinical white enamel)
        thermal_capacitance: float = 420000.0, # J / K - Thermal mass of payload + PCM packs + internal air
        rated_chiller_power: float = 3600.0,   # W - Rated maximum cooling capacity
        door_leakage_coeff: float = 450.0      # W / K - Convective thermal infiltration when doors open
    ):
        self.u_wall = u_wall
        self.surface_area = surface_area
        self.roof_area = roof_area
        self.solar_absorptivity = solar_absorptivity
        self.thermal_capacitance = thermal_capacitance
        self.rated_chiller_power = rated_chiller_power
        self.door_leakage_coeff = door_leakage_coeff

    def step(
        self,
        dt_seconds: float,
        t_current: float,
        t_ambient: float,
        solar_flux_w_m2: float = 0.0,
        chiller_state: str = "NORMAL",
        door_state: str = "CLOSED",
        target_setpoint: float = 4.0
    ) -> Dict[str, Any]:
        """
        Advances thermal state forward by dt_seconds.
        Returns: {
            't_next': float,
            'delta_t': float,
            'q_cond_w': float,
            'q_solar_w': float,
            'q_door_w': float,
            'q_cooling_w': float,
            'q_net_w': float
        }
        """
        delta_t_amb = t_ambient - t_current

        # 1. Fourier Conduction through insulated sandwich panels
        q_cond = self.u_wall * self.surface_area * delta_t_amb

        # 2. Solar Radiation Heat Gain on container roof
        q_solar = self.solar_absorptivity * self.roof_area * max(0.0, solar_flux_w_m2)

        # 3. Air Infiltration / Door Opening Leakage
        if door_state.upper() == "OPEN":
            q_door = self.door_leakage_coeff * delta_t_amb
        else:
            q_door = 0.0

        # Total thermal ingress into payload compartment
        q_ingress = q_cond + q_solar + q_door

        # 4. Active Refrigeration Chiller Heat Extraction
        if chiller_state.upper() == "NORMAL":
            # Proportional chiller controller keeping cargo near setpoint (2°C - 8°C)
            temp_error = t_current - target_setpoint
            proportional_cooling = q_ingress + (300.0 * temp_error)
            q_cooling = min(self.rated_chiller_power, max(0.0, proportional_cooling))
        elif chiller_state.upper() == "DEGRADED":
            # Degraded compressor (reduced RPM / low refrigerant)
            # Regulates around target setpoint (e.g. 9.4°C excursion) with proportional control
            temp_error = t_current - target_setpoint
            proportional_cooling = q_ingress + (200.0 * temp_error)
            q_cooling = min(self.rated_chiller_power, max(0.0, proportional_cooling))
        elif chiller_state.upper() in ["FAILED", "OFF"]:
            # Total refrigeration failure - zero cooling
            q_cooling = 0.0
        else:
            q_cooling = 0.0

        q_net = q_ingress - q_cooling

        # Thermal inertia differential equation
        delta_t = (q_net * dt_seconds) / self.thermal_capacitance
        t_next = t_current + delta_t

        # Physics bounds: payload compartment temperature is bounded by sol-air equilibrium
        # (cannot heat beyond ambient + 3.5°C in insulated reefer, capped at 42.0°C max Indian asphalt ambient)
        # or drop below active refrigeration floor (-25.0°C deep freeze, -2.0°C chilled)
        t_soak_max = min(42.0, t_ambient + 3.5)
        t_next = max(-25.0, min(t_soak_max, t_next))

        return {
            "t_next": round(t_next, 4),
            "delta_t": round(delta_t, 4),
            "q_cond_w": round(q_cond, 2),
            "q_solar_w": round(q_solar, 2),
            "q_door_w": round(q_door, 2),
            "q_cooling_w": round(q_cooling, 2),
            "q_net_w": round(q_net, 2)
        }
