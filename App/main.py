from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.watchlist import Watchlist
from app.store import FeatureStore
from app.scoring import RiskScorer

app = FastAPI(title="Camera Behavioral Risk Engine (Demo)")

watchlist = Watchlist(csv_path="watchlist.csv")
store = FeatureStore(redis_url="redis://localhost:6379/0")
scorer = RiskScorer()

class CameraEvent(BaseModel):
    ts: str = Field(..., description="ISO timestamp")
    branch_id: str
    camera_id: str
    entity_type: str = Field(..., description="person|vehicle")
    entity_id: str = Field(..., description="stable id: face_id or plate or vendor id")
    face_id: str | None = None
    plate: str | None = None
    roi: str | None = None
    dwell_sec: int | None = None

@app.post("/event")
def ingest_event(event: CameraEvent):
    # 1) Watchlist
    watchlisted = watchlist.is_watchlisted(event.entity_type, event.face_id, event.plate)

    # 2) Counters
    features = store.update(event.branch_id, event.entity_id, event.roi, event.dwell_sec)

    # 3) Risk scoring
    result = scorer.score(features=features, watchlisted=watchlisted, entity_type=event.entity_type)

    return {
        "event": event.model_dump(),
        "watchlisted": watchlisted,
        "features": features,
        "result": result
    }

@app.post("/watchlist/reload")
def reload_watchlist():
    watchlist.reload()
    return {"status": "ok", "faces": len(watchlist.face_ids), "plates": len(watchlist.plates)}

@app.get("/health")
def health():
    return {"status": "ok"}
