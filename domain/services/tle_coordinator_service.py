from datetime import datetime, timedelta, timezone
from typing import List, Optional
from domain.interfaces.tle_repository_interface import TLERepositoryInterface
from domain.interfaces.tle_service_interface import TLEServiceInterface
from domain.models.tle_entry import TLEEntry
from infrastructure.utils.tle_parser import TLEParser


# One way to improve this would be to have a seprate service for the logic for the fetching and another for the storing
# This would lead to more decoupled code and easier to test
class TLECoordinatorService:
    def __init__(
        self, 
        repository: TLERepositoryInterface,
        service: TLEServiceInterface,
        refresh_interval_hours: int = 1
    ):
        self.repository = repository
        self.service = service
        self.refresh_interval = timedelta(hours=refresh_interval_hours)
    
    def get_latest_tle(self, norad_id: str) -> Optional[TLEEntry]:
        now = datetime.now(timezone.utc)
        existing_tle = self.repository.get_latest_tle(norad_id)

        needs_refresh = False
        if existing_tle is None:
            needs_refresh = True
        else:
            fetch_time = existing_tle.fetched_at
            if fetch_time.tzinfo is None:
                fetch_time = fetch_time.replace(tzinfo=timezone.utc)
            time_since_fetch = now - fetch_time
            needs_refresh = time_since_fetch >= self.refresh_interval

        if needs_refresh:
            tle = self.service.fetch_tle(norad_id)
            if tle:
                if not tle.epoch:
                    tle = TLEParser.parse_tle(tle.line1, tle.line2)
                self.repository.store_tle(tle, "celestrak", now)

        return self.repository.get_latest_tle(norad_id)
    
    def get_tle_history(self, norad_id: str) -> List[TLEEntry]:
        return self.repository.get_tle_history(norad_id)
    
    def add_custom_tle(self, norad_id: str, line1: str, line2: str) -> Optional[TLEEntry]:
        if not TLEParser.validate_tle(line1, line2):
            return None
        
        try:
            tle = TLEParser.parse_tle(line1, line2)
            if tle.norad_id != norad_id:
                return None
            
            now = datetime.now(timezone.utc)
            self.repository.store_tle(tle, "client", now)
            return TLEEntry(tle=tle, source="client", fetched_at=now, stored_at=now)
        except Exception as e:
            print(f"Error parsing custom TLE: {e}")
            return None
