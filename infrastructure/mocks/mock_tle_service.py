from typing import Optional
from domain.interfaces.tle_service_interface import TLEServiceInterface
from domain.models.tle import TLE

class MockTLEService(TLEServiceInterface):
    def __init__(self):
        self.mock_data = {
            "54234": TLE(
                line1="1 54234U 22150A   26025.23306172  .00000191  00000+0  11139-3 0  9995",
                line2="2 54234  98.7509 326.0095 0000754 215.9195 144.1931 14.19539113166262"
            ),
            "12345": TLE(
                line1="1 12345U 24022A   24211.20428626  .00001782  00000+0  38520-3 0  9993",
                line2="2 12345  98.3320 160.7411 0001541  53.5545  58.5641 14.59534437182847"
            )
        }
    
    def fetch_tle(self, norad_id: str) -> Optional[TLE]:
        return self.mock_data.get(norad_id)