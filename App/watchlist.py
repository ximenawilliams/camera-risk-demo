import pandas as pd
from pathlib import Path

class Watchlist:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.face_ids = set()
        self.plates = set()
        self.reload()

    def reload(self):
        if not self.csv_path.exists():
            self.face_ids, self.plates = set(), set()
            return

        df = pd.read_csv(self.csv_path)
        self.face_ids = set(df["face_id"].dropna().astype(str)) if "face_id" in df.columns else set()
        self.plates = set(df["plate"].dropna().astype(str)) if "plate" in df.columns else set()

    def is_watchlisted(self, entity_type: str, face_id: str | None, plate: str | None) -> bool:
        if entity_type == "person" and face_id and str(face_id) in self.face_ids:
            return True
        if entity_type == "vehicle" and plate and str(plate) in self.plates:
            return True
        return False
