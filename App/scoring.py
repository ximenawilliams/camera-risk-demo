import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "anomaly_model.joblib"

class RiskScorer:
    def __init__(self):
        if not MODEL_PATH.exists():
            self.model = None
        else:
            self.model = joblib.load(MODEL_PATH)

    def score(self, features: dict, watchlisted: bool, entity_type: str) -> dict:
        # Reglas base (auditables)
        risk = 0
        reasons = []

        if watchlisted:
            risk += 70
            reasons.append("watchlist_match")

        # reglas comportamentales simples
        if entity_type == "vehicle" and features["visits_24h"] >= 3:
            risk += 15
            reasons.append("vehicle_many_visits_24h")

        if entity_type == "person" and features["corner_loiter_sec_24h"] > 8 * 60:
            risk += 25
            reasons.append("person_corner_loitering")

        # ML: anomalía (si hay modelo)
        ml = {"anomaly": None, "anomaly_score": None}
        if self.model is not None:
            X = [[
                features["visits_24h"],
                features["dwell_sec_24h"],
                features["corner_loiter_sec_24h"],
                1 if watchlisted else 0,
                features["hour"]
            ]]

            # IsolationForest: predict -> -1 anomalía, 1 normal
            pred = int(self.model.predict(X)[0])
            # score_samples: más bajo => más anómalo
            anomaly_score = float(self.model.named_steps["model"].score_samples(
                self.model.named_steps["scaler"].transform(X)
            )[0])

            is_anomaly = (pred == -1)
            ml = {"anomaly": is_anomaly, "anomaly_score": anomaly_score}

            if is_anomaly:
                risk += 10
                reasons.append("ml_anomaly")

        # normaliza a 0..100
        risk = min(100, risk)

        alert_level = "LOW"
        if risk >= 80:
            alert_level = "HIGH"
        elif risk >= 50:
            alert_level = "MEDIUM"

        return {
            "risk_score": risk,
            "alert_level": alert_level,
            "reasons": reasons,
            "ml": ml
        }
