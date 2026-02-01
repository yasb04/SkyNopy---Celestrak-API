from datetime import datetime, timezone
from typing import Dict, List, Optional
from domain.models.tle import TLE
from domain.models.tle_entry import TLEEntry
from domain.interfaces.tle_repository_interface import TLERepositoryInterface


class TLEStorage(TLERepositoryInterface):
    def __init__(self):
        self.storage: Dict[str, Dict] = {}

    @staticmethod
    def _epoch_key(tle_dict: Dict) -> datetime:
        epoch_str = tle_dict.get("epoch")
        if not epoch_str:
            return datetime.min.replace(tzinfo=timezone.utc)

        if isinstance(epoch_str, str) and epoch_str.endswith("Z"):
            epoch_str = epoch_str[:-1] + "+00:00"

        try:
            dt = datetime.fromisoformat(epoch_str)
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    
    def get_latest_tle(self, norad_id: str) -> Optional[TLEEntry]:
        if norad_id not in self.storage or not self.storage[norad_id]["tles"]:
            return None
        
        tles = self.storage[norad_id]["tles"]
        sorted_tles = sorted(
            tles,
            key=lambda x: (self._epoch_key(x), x.get("stored_at", "")),
            reverse=True
        )
        return TLEEntry.from_dict(sorted_tles[0])
    
    def get_tle_history(self, norad_id: str) -> List[TLEEntry]:
        if norad_id not in self.storage:
            return []
        
        tles = self.storage[norad_id]["tles"].copy()
        sorted_tles = sorted(
            tles,
            key=lambda x: (self._epoch_key(x), x.get("stored_at", "")),
            reverse=True
        )
        return [TLEEntry.from_dict(tle_dict) for tle_dict in sorted_tles]
    
    def get_latest_fetch_time(self, norad_id: str) -> Optional[datetime]:
        if norad_id not in self.storage:
            return None
        return self.storage[norad_id].get("latest_fetch")
    
    def store_tle(self, tle: TLE, source: str, fetched_at: datetime):
        norad_id = tle.norad_id
        if norad_id not in self.storage:
            self.storage[norad_id] = {
                "tles": [],
                "latest_fetch": None
            }
        
        tle_entry = TLEEntry(
            tle=tle,
            source=source,
            fetched_at=fetched_at,
            stored_at=datetime.now(timezone.utc)
        )
        
        self.storage[norad_id]["tles"].append(tle_entry.to_dict())
        if source == "celestrak":
            if (self.storage[norad_id]["latest_fetch"] is None or 
                fetched_at > self.storage[norad_id]["latest_fetch"]):
                self.storage[norad_id]["latest_fetch"] = fetched_at
