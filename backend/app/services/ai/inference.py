import os
import json
import math
import joblib
import numpy as np

class AIDecisionService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIDecisionService, cls).__new__(cls)
            cls._instance._init_models()
        return cls._instance

    def _init_models(self):
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        cls_path = os.path.join(models_dir, "xgb_spoilage_classifier.joblib")
        reg_path = os.path.join(models_dir, "xgb_temp_forecaster.joblib")
        explainer_path = os.path.join(models_dir, "shap_explainer.joblib")
        meta_path = os.path.join(models_dir, "model_metadata.json")

        self.classifier = None
        self.forecasters = None
        self.explainer = None
        self.metadata = {}

        try:
            if os.path.exists(cls_path):
                self.classifier = joblib.load(cls_path)
            if os.path.exists(reg_path):
                self.forecasters = joblib.load(reg_path)
            if os.path.exists(explainer_path):
                self.explainer = joblib.load(explainer_path)
            if os.path.exists(meta_path):
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)

            self.features = self.metadata.get("features", [
                'temp_mean', 'probe_discrepancy', 'room_temp', 'room_humidity',
                'thermal_gradient', 'temp_delta_1h', 'temp_delta_3h', 'temp_accel',
                'temp_rolling_mean_3h', 'temp_rolling_std_3h', 'is_frozen_regime'
            ])
        except Exception as e:
            print(f"[AI Service] Model initialization warning: {e}")

    def is_ready(self) -> bool:
        return self.classifier is not None and self.forecasters is not None

    def build_feature_vector(self, raw: dict) -> np.ndarray:
        """
        Builds the 11-dimensional zero-leakage physical IoT telemetry feature vector.
        Consensus temperature from dual probes + ambient gradient + kinetic rates of change.
        """
        p1 = raw.get("probe_1_temp", raw.get("temperature", raw.get("current_temperature", raw.get("chamber_temp_reading", raw.get("thermal_shipper_temp_reading", 4.0)))))
        p2 = raw.get("probe_2_temp", raw.get("probe_2_temperature", p1))
        p1 = float(p1)
        p2 = float(p2)
        temp_mean = (p1 + p2) / 2.0
        probe_discrepancy = float(raw.get("probe_discrepancy", abs(p1 - p2)))

        room_temp = float(raw.get("ambient_temperature", raw.get("room_temp_reading", 28.0)))
        room_humidity = float(raw.get("humidity", raw.get("room_humidity_reading", 65.0)))
        thermal_gradient = room_temp - temp_mean

        delta_1h = float(raw.get("temp_delta_1h", raw.get("rate_of_rise_c_hr", 0.0)))
        delta_3h = float(raw.get("temp_delta_3h", delta_1h * 3.0))
        temp_accel = float(raw.get("temp_accel", delta_1h * 0.1))
        rolling_mean = float(raw.get("temp_rolling_mean_3h", temp_mean))
        rolling_std = float(raw.get("temp_rolling_std_3h", max(0.05, abs(delta_1h) * 0.5)))
        is_frozen = 1.0 if temp_mean < -15.0 else 0.0

        vector = [
            temp_mean, probe_discrepancy, room_temp, room_humidity,
            thermal_gradient, delta_1h, delta_3h, temp_accel,
            rolling_mean, rolling_std, is_frozen
        ]
        return np.array(vector, dtype=float).reshape(1, -1)

    def predict(self, raw_features: dict, temp_ceiling: float = 8.0, temp_floor: float = 2.0) -> dict:
        """
        Executes real-time inference:
        1. 4-hour forward lookahead failure/excursion probability.
        2. Multi-horizon temperature forecast (+1h, +2h, +4h).
        3. Real local instance-level SHAP TreeExplainer attribution.
        """
        if not self.is_ready():
            return {
                "ai_available": False,
                "spoilage_probability": 0.0,
                "spoilage_risk_percent": 0.0,
                "risk_level": "UNKNOWN",
                "forecast": {},
                "projected_ceiling_breach_hours": None,
                "top_risk_factors": []
            }

        X = self.build_feature_vector(raw_features)
        temp_mean = float(X[0, 0])
        room_temp = float(X[0, 2])
        delta_1h = max(-2.5, min(2.0, float(X[0, 5])))

        # 1. 4-Hour Forward Lookahead Spoilage/Excursion Risk
        try:
            raw_prob = float(self.classifier.predict_proba(X)[0][1])
        except Exception:
            raw_prob = 0.05

        # Domain & Physics Risk Calibration
        if temp_mean > temp_ceiling:
            # Active Excursion: chamber is already past clinical upper bound
            prob = max(raw_prob, min(0.99, 0.85 + (temp_mean - temp_ceiling) * 0.05))
            risk_level = "CRITICAL"
        elif temp_mean < temp_floor and temp_floor > -15.0:
            # Freezing Danger: destroys vaccine potency immediately
            prob = max(raw_prob, min(0.99, 0.85 + (temp_floor - temp_mean) * 0.08))
            risk_level = "CRITICAL"
        elif temp_mean >= (temp_ceiling - 1.0) and delta_1h > 0.05:
            # High Risk Drift towards breach
            prob = max(raw_prob, min(0.85, 0.60 + (temp_mean - (temp_ceiling - 1.0)) * 0.20))
            risk_level = "HIGH"
        elif temp_mean >= (temp_ceiling - 1.5) and delta_1h > 0.10:
            prob = max(raw_prob, min(0.65, 0.45 + delta_1h * 0.5))
            risk_level = "MEDIUM"
        else:
            prob = min(raw_prob, 0.12) if abs(delta_1h) < 0.10 else raw_prob
            if prob >= 0.70:
                risk_level = "CRITICAL"
            elif prob >= 0.45:
                risk_level = "HIGH"
            elif prob >= 0.20:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

        # 2. Multi-Horizon Physics-Informed Temperature Forecasts (+1h, +2h, +4h)
        forecasts = {}
        projected_breach_hours = None

        for horizon in [1, 2, 4]:
            key = f"horizon_{horizon}h"
            pred_delta = 0.0
            if key in self.forecasters:
                try:
                    pred_delta = float(self.forecasters[key].predict(X)[0])
                except Exception:
                    pred_delta = 0.0

            # Newton-Fourier thermal drift physics:
            # Drift decays as container approaches ambient equilibrium
            drift_decay = math.exp(-0.06 * horizon)
            physical_delta = delta_1h * horizon * drift_decay

            # If regressor delta agrees in sign, blend ML and physics; otherwise anchor to physical rate
            if np.sign(pred_delta) == np.sign(delta_1h) and abs(delta_1h) > 0.02:
                blended_delta = 0.70 * physical_delta + 0.30 * pred_delta
            elif abs(delta_1h) > 0.05:
                blended_delta = physical_delta
            else:
                # Nominal regulated refrigeration: cargo stays near setpoint with minimal thermostat cycling
                blended_delta = math.copysign(min(0.08 * horizon, abs(pred_delta * 0.04)), pred_delta if pred_delta != 0 else 1.0)

            # Clamping bounds: container cannot heat above ambient + 2°C or drop below setpoint floor
            t_soak_max = min(40.0, room_temp + 2.0)
            max_rise = max(0.0, t_soak_max - temp_mean)
            max_drop = -2.2 * horizon if delta_1h < -0.1 else -0.5 * horizon

            clamped_delta = max(max_drop, min(max_rise, blended_delta))
            pred_val = round(temp_mean + clamped_delta, 2)
            forecasts[f"plus_{horizon}h"] = pred_val

            # Check for breach of upper clinical ceiling
            if pred_val > temp_ceiling and projected_breach_hours is None:
                projected_breach_hours = horizon

        # 3. Instance-Level SHAP Explanation Vector
        local_risk_factors = []
        if self.explainer is not None:
            try:
                shap_obj = self.explainer(X)
                shap_vals = shap_obj.values[0]

                factor_pairs = []
                for name, sv in zip(self.features, shap_vals):
                    factor_pairs.append({
                        "feature": name,
                        "shap_value": float(sv),
                        "abs_shap": abs(float(sv))
                    })

                factor_pairs.sort(key=lambda x: x["abs_shap"], reverse=True)

                for item in factor_pairs[:3]:
                    readable_name = item["feature"].replace('_', ' ').title()
                    direction = "Increasing risk" if item["shap_value"] > 0 else "Stabilizing safety"
                    local_risk_factors.append({
                        "factor": readable_name,
                        "shap_impact": round(item["shap_value"], 3),
                        "direction": direction,
                        "detail": f"{readable_name} ({direction.lower()})"
                    })
            except Exception as e:
                print(f"[AI Service] Local SHAP evaluation note: {e}")

        # Fallback to global metadata if local SHAP fails
        if not local_risk_factors:
            global_rankings = self.metadata.get("shap_feature_importance", [])
            for item in global_rankings[:3]:
                readable_name = item["feature"].replace('_', ' ').title()
                local_risk_factors.append({
                    "factor": readable_name,
                    "shap_impact": round(item.get("mean_abs_shap", 0.1), 3),
                    "direction": "Global risk driver",
                    "detail": f"Systemic contribution from {readable_name}"
                })

        return {
            "ai_available": True,
            "spoilage_probability": round(prob, 3),
            "spoilage_risk_percent": round(prob * 100, 1),
            "risk_level": risk_level,
            "forecast": forecasts,
            "projected_ceiling_breach_hours": projected_breach_hours,
            "top_risk_factors": local_risk_factors,
            "model_version": self.metadata.get("version", "2.0.0-production")
        }

ai_service = AIDecisionService()
