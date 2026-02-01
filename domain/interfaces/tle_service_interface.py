from abc import ABC, abstractmethod
from typing import Optional
from domain.models.tle import TLE

class TLEServiceInterface(ABC):
    @abstractmethod
    def fetch_tle(self, norad_id: str) -> Optional[TLE]:
        pass