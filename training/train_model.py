import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib
from pathlib import Path

DATA_PATH = Path(__file__).parent / "sample_training.csv"
OUT_PATH = Path(__file__).parent.parent / "app" / "anomaly_model.joblib"

df = pd.read_csv(DATA_PATH)

X = df[["visits_24h", "dwell_sec_24h", "corner_loiter_sec_24h", "watchlisted", "hour"]]

pipe = Pipeline(steps=[
    ("scaler", StandardScaler()),
    ("model", IsolationForest(
        n_estimators=300,
        contamination=0.12,   # ajusta según cuántos "raros" esperas
        random_state=42
    ))
])

pipe.fit(X)
joblib.dump(pipe, OUT_PATH)
print(f"✅ Modelo guardado en {OUT_PATH}")
