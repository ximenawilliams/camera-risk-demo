import json
import redis
from datetime import datetime, timezone

def utc_hour() -> int:
    return datetime.now(timezone.utc).hour

class FeatureStore:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    def _key(self, branch_id: str, entity_id: str) -> str:
        return f"feat:{branch_id}:{entity_id}"

    def get(self, branch_id: str, entity_id: str) -> dict:
        raw = self.r.get(self._key(branch_id, entity_id))
        return json.loads(raw) if raw else {
            "visits_24h": 0,
            "dwell_sec_24h": 0,
            "corner_loiter_sec_24h": 0,
            "hour": utc_hour()
        }

    def update(self, branch_id: str, entity_id: str, roi: str | None, dwell_sec: int | None) -> dict:
        key = self._key(branch_id, entity_id)
        s = self.get(branch_id, entity_id)

        # Visita (en un sistema real esto sería por "sesión", aquí es demo)
        s["visits_24h"] += 1

        if dwell_sec:
            s["dwell_sec_24h"] += int(dwell_sec)

        if roi == "corner" and dwell_sec:
            s["corner_loiter_sec_24h"] += int(dwell_sec)

        s["hour"] = utc_hour()

        self.r.set(key, json.dumps(s))
        self.r.expire(key, 24 * 3600)  # 24h
        return s
