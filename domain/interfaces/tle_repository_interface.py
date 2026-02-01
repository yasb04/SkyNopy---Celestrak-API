from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from domain.models.tle import TLE
from domain.models.tle_entry import TLEEntry


class TLERepositoryInterface(ABC):
    
    @abstractmethod
    def get_latest_tle(self, norad_id: str) -> Optional[TLEEntry]:
        pass

    @abstractmethod
    def get_tle_history(self, norad_id: str) -> List[TLEEntry]:
        pass

    @abstractmethod
    def store_tle(self, tle: TLE, source: str, fetched_at: datetime):
        pass
