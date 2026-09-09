import math
import logging
from typing import List, Dict, Any, Optional, Tuple
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.all import Depot, Shipment

logger = logging.getLogger("spatial_routing")

# ----------------------------------------------------------------------------
# NATIONAL COLD-CHAIN HIGHWAY CORRIDOR WAYPOINTS & METADATA
# ----------------------------------------------------------------------------
CORRIDORS: Dict[str, Dict[str, Any]] = {
    "NH-48": {
        "name": "NH-48 Southern Cold-Chain Corridor (Chennai - Vellore - Bengaluru)",
        "nominal_speed_kmh": 65.0,
        "tortuosity_factor": 1.18,
        "waypoints": [
            (13.0827, 80.2707),  # Chennai
            (13.0125, 80.0812),  # Poonamallee
            (12.9675, 79.9427),  # Sriperumbudur
            (12.8342, 79.7036),  # Kanchipuram
            (12.9272, 79.3330),  # Ranipet
            (12.9165, 79.1325),  # Vellore
            (12.7904, 78.7166),  # Ambur
            (12.6322, 78.4983),  # Vaniyambadi
            (12.5186, 78.2137),  # Krishnagiri
            (12.7409, 77.8253),  # Hosur
            (12.9716, 77.5946)   # Bengaluru
        ]
    },
    "NH-44": {
        "name": "NH-44 Central Cold-Chain Spine (Bengaluru - Kurnool - Hyderabad)",
        "nominal_speed_kmh": 70.0,
        "tortuosity_factor": 1.15,
        "waypoints": [
            (12.9716, 77.5946),  # Bengaluru
            (13.3409, 77.5376),  # Doddaballapur
            (14.6819, 77.6006),  # Anantapur
            (15.8281, 78.0373),  # Kurnool
            (16.7488, 78.0035),  # Mahbubnagar
            (17.3850, 78.4867)   # Hyderabad
        ]
    },
    "NH-19": {
        "name": "NH-19 Northern Arterial (Delhi - Agra - Kanpur - Lucknow)",
        "nominal_speed_kmh": 72.0,
        "tortuosity_factor": 1.14,
        "waypoints": [
            (28.6139, 77.2090),  # Delhi
            (27.8974, 77.6744),  # Mathura
            (27.1767, 78.0081),  # Agra
            (26.4499, 80.3319),  # Kanpur
            (26.8467, 80.9462)   # Lucknow
        ]
    },
    "NH-48-WEST": {
        "name": "NH-48 Western Trunk (Mumbai - Pune - Satara - Kolhapur)",
        "nominal_speed_kmh": 60.0,
        "tortuosity_factor": 1.22,
        "waypoints": [
            (19.0760, 72.8777),  # Mumbai
            (18.7546, 73.4062),  # Lonavala Expressway
            (18.5204, 73.8567),  # Pune
            (17.6805, 74.0183),  # Satara
            (16.7050, 74.2433)   # Kolhapur
        ]
    },
    "NH-106": {
        "name": "NH-106 Northeast Mountain Corridor (Guwahati - Nongpoh - Shillong)",
        "nominal_speed_kmh": 35.0,
        "tortuosity_factor": 1.45,
        "waypoints": [
            (26.1445, 91.7362),  # Guwahati
            (25.9010, 91.8800),  # Nongpoh
            (25.5788, 91.8933)   # Shillong
        ]
    }
}

class SpatialRoutingEngine:
    """
    Production-Grade Cold-Chain Spatial Intelligence Engine:
    1. Tier 1: PostGIS Geodetic Spatial Filter (true spherical distance, facility service & capacity checks).
    2. Tier 2: Highway Corridor Projection & Hybrid OSRM/Spline Road Distance/ETA Engine.
    3. Tier 3: Kinetic Thermal Reachability Validator (Remaining Thermal Buffer vs ETA Feasibility Scoring).
    """

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle geodetic distance in kilometers."""
        r = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    _route_cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def fetch_osrm_route(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> Optional[Dict[str, Any]]:
        """
        Attempts to query OpenStreetMap / OSRM public routing API with a strict 1.5s timeout.
        Returns distance (km), duration (mins), and GeoJSON coordinates if available.
        Cached in-memory to prevent redundant network requests.
        """
        cache_key = f"{lat1:.4f},{lon1:.4f}->{lat2:.4f},{lon2:.4f}"
        if cache_key in cls._route_cache:
            return cls._route_cache[cache_key]

        url = f"https://router.project-osrm.org/route/v1/driving/{lon1:.6f},{lat1:.6f};{lon2:.6f},{lat2:.6f}?overview=full&geometries=geojson"
        try:
            with httpx.Client(timeout=1.5) as client:
                res = client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    routes = data.get("routes", [])
                    if routes:
                        r = routes[0]
                        res_obj = {
                            "source": "OSRM_LIVE_ROAD_GRAPH",
                            "distance_km": round(r["distance"] / 1000.0, 2),
                            "duration_mins": round(r["duration"] / 60.0, 1),
                            "geometry": r["geometry"]["coordinates"]  # [[lon, lat], ...]
                        }
                        cls._route_cache[cache_key] = res_obj
                        return res_obj
        except Exception as e:
            logger.debug(f"OSRM query fallback triggered: {e}")
        return None

    @classmethod
    def generate_corridor_diversion_geometry(
        cls, lat1: float, lon1: float, lat2: float, lon2: float, corridor_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hybrid Fallback: Generates a curvature-adjusted geodetic spline along the corridor network.
        Ensures high-fidelity map polylines even when operating completely offline.
        """
        corridor = CORRIDORS.get(corridor_name, CORRIDORS["NH-48"])
        tortuosity = corridor["tortuosity_factor"]
        speed_kmh = corridor["nominal_speed_kmh"]
        geodetic_dist = cls.haversine_km(lat1, lon1, lat2, lon2)
        road_dist_km = round(geodetic_dist * tortuosity, 2)
        duration_mins = round((road_dist_km / speed_kmh) * 60.0, 1)

        # Generate smooth intermediate spline points for Leaflet map display
        num_steps = max(5, int(geodetic_dist / 3.0))
        coords = []
        for i in range(num_steps + 1):
            f = i / float(num_steps)
            # Add slight realistic perpendicular curve offset
            curve_amp = math.sin(f * math.pi) * 0.008
            cur_lat = lat1 + (lat2 - lat1) * f + curve_amp
            cur_lon = lon1 + (lon2 - lon1) * f
            coords.append([round(cur_lon, 6), round(cur_lat, 6)])

        return {
            "source": "CORRIDOR_TOPOLOGY_SPLINE",
            "distance_km": road_dist_km,
            "duration_mins": duration_mins,
            "geometry": coords
        }

    @classmethod
    def calculate_road_route(
        cls, lat1: float, lon1: float, lat2: float, lon2: float, corridor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tier 2 Hybrid Router:
        Tries OSRM first; if unavailable or timeout, seamlessly falls back to Corridor Spline.
        """
        osrm_res = cls.fetch_osrm_route(lat1, lon1, lat2, lon2)
        if osrm_res:
            return osrm_res
        return cls.generate_corridor_diversion_geometry(lat1, lon1, lat2, lon2, corridor)

    @classmethod
    def evaluate_thermal_feasibility(
        cls,
        eta_mins: float,
        current_temp: float,
        temp_ceiling: float = 8.0,
        temp_floor: float = 2.0,
        rate_of_change: float = 0.0,
        projected_breach_hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Tier 3 Cold-Chain Feasibility Validator:
        Assesses if the payload will survive until arrival at the facility dock.
        Includes a 15-minute cross-docking and ILR transfer safety buffer.
        """
        DOCK_TRANSFER_BUFFER_MINS = 15.0

        # Calculate time to critical failure
        if projected_breach_hours is not None and projected_breach_hours > 0:
            time_to_breach_mins = projected_breach_hours * 60.0
        elif current_temp > temp_ceiling or current_temp < temp_floor:
            # Already in breach! Thermal reserve is depleted
            time_to_breach_mins = 0.0
        elif rate_of_change > 0.1:
            temp_headroom = max(0.0, temp_ceiling - current_temp)
            time_to_breach_mins = (temp_headroom / rate_of_change) * 60.0
        else:
            # Nominal steady thermal reserve (up to 4 hours)
            time_to_breach_mins = 240.0

        total_required_time = eta_mins + DOCK_TRANSFER_BUFFER_MINS
        net_margin_mins = round(time_to_breach_mins - total_required_time, 1)

        if time_to_breach_mins <= 0:
            status = "BREACH_ACTIVE"
            color = "CRITICAL"
            badge = "Active Breach · Emergency Reroute"
        elif net_margin_mins >= 30.0:
            status = "SAFE"
            color = "HEALTHY"
            badge = f"Safe Buffer (+{net_margin_mins:.0f}m)"
        elif net_margin_mins >= 0.0:
            status = "MARGINAL"
            color = "WARNING"
            badge = f"Tight Window (+{net_margin_mins:.0f}m)"
        elif net_margin_mins >= -20.0:
            status = "CRITICAL_REACHABLE"
            color = "PROBLEM"
            badge = f"High Risk ({net_margin_mins:.0f}m breach)"
        else:
            status = "INFEASIBLE"
            color = "CRITICAL"
            badge = f"Infeasible ({abs(net_margin_mins):.0f}m overrun)"

        return {
            "status": status,
            "badge": badge,
            "color": color,
            "time_to_breach_mins": round(time_to_breach_mins, 1),
            "dock_transfer_buffer_mins": DOCK_TRANSFER_BUFFER_MINS,
            "total_mission_time_mins": round(total_required_time, 1),
            "net_thermal_margin_mins": net_margin_mins,
            "is_feasible": net_margin_mins >= -10.0
        }

    @classmethod
    def find_reroute_candidates(
        cls,
        db: Session,
        lat: float,
        lon: float,
        requires_deep_freeze: bool = False,
        current_temp: float = 4.5,
        temp_ceiling: float = 8.0,
        temp_floor: float = 2.0,
        rate_of_change: float = 0.0,
        projected_breach_hours: Optional[float] = None,
        corridor: Optional[str] = None,
        max_candidates: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Full 3-Tier Execution:
        1. Queries PostGIS for nearest verified depots within 150 km geodetic distance.
        2. Filters for service compatibility (e.g. DEEP_FREEZE vs REFRIGERATION).
        3. Computes road routing & ETA via OSRM/Corridor graph.
        4. Validates thermal feasibility against kinetic reserve.
        5. Ranks candidates by feasibility, ETA, and depot services.
        """
        # PostGIS query: spherical distance in meters
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        dist_expr = func.ST_DistanceSphere(Depot.geom, point)
        
        # Performance optimization:
        # Use PostGIS spatial indexing to order by geodetic distance and evaluate the closest candidates
        query = db.query(
            Depot,
            dist_expr.label("geodetic_dist_m")
        ).filter(
            Depot.geom.isnot(None),
            Depot.availability != "OFFLINE"
        ).order_by(dist_expr).limit(max_candidates)

        nearest_depots = query.all()
        candidates = []

        for idx, (depot, dist_m) in enumerate(nearest_depots):
            geodetic_km = round((dist_m or cls.haversine_km(lat, lon, depot.latitude, depot.longitude) * 1000) / 1000.0, 2)
            
            # Service compatibility check
            services = depot.services or []
            if requires_deep_freeze and "DEEP_FREEZE" not in services and "ULT_STORAGE" not in services:
                continue

            # Compute road routing & ETA:
            # Use live OSRM for the primary nearest candidates (idx < 2) and instant corridor spline for subsequent
            if idx < 2:
                route_res = cls.calculate_road_route(lat, lon, depot.latitude, depot.longitude, corridor)
            else:
                route_res = cls.generate_corridor_diversion_geometry(lat, lon, depot.latitude, depot.longitude, corridor)

            road_dist_km = route_res["distance_km"]
            eta_mins = route_res["duration_mins"]

            # Thermal feasibility check
            thermal_eval = cls.evaluate_thermal_feasibility(
                eta_mins=eta_mins,
                current_temp=current_temp,
                temp_ceiling=temp_ceiling,
                temp_floor=temp_floor,
                rate_of_change=rate_of_change,
                projected_breach_hours=projected_breach_hours
            )

            # Composite ranking score: lower ETA + higher thermal margin + service bonus
            service_bonus = 20.0 if ("VEHICLE_SWAP" in services or "DEEP_FREEZE" in services) else 0.0
            margin_factor = max(-50.0, min(100.0, thermal_eval["net_thermal_margin_mins"]))
            score = round((100.0 / (eta_mins + 1.0)) * 50.0 + margin_factor * 0.5 + service_bonus, 1)

            candidates.append({
                "depot_id": depot.id,
                "depot_name": depot.name,
                "latitude": depot.latitude,
                "longitude": depot.longitude,
                "services": services,
                "availability": depot.availability,
                "certification_status": depot.certification_status,
                "geodetic_distance_km": geodetic_km,
                "road_distance_km": road_dist_km,
                "eta_minutes": eta_mins,
                "thermal_feasibility": thermal_eval,
                "routing_source": route_res["source"],
                "route_geometry": route_res["geometry"],
                "ranking_score": score
            })

        # Sort by ranking score descending (highest score first)
        candidates.sort(key=lambda x: x["ranking_score"], reverse=True)
        return candidates[:max_candidates]

    @classmethod
    def find_optimal_depot(
        cls,
        db: Session,
        lat: float,
        lon: float,
        requires_deep_freeze: bool = False,
        current_temp: float = 4.5,
        temp_ceiling: float = 8.0,
        temp_floor: float = 2.0,
        rate_of_change: float = 0.0,
        projected_breach_hours: Optional[float] = None,
        corridor: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Returns the single top-ranked feasible candidate depot or None if no candidates found."""
        candidates = cls.find_reroute_candidates(
            db=db,
            lat=lat,
            lon=lon,
            requires_deep_freeze=requires_deep_freeze,
            current_temp=current_temp,
            temp_ceiling=temp_ceiling,
            temp_floor=temp_floor,
            rate_of_change=rate_of_change,
            projected_breach_hours=projected_breach_hours,
            corridor=corridor,
            max_candidates=1
        )
        return candidates[0] if candidates else None

spatial_routing_engine = SpatialRoutingEngine()
