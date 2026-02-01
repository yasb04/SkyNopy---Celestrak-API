from typing import Optional
import requests
from domain.interfaces.tle_service_interface import TLEServiceInterface
from domain.models.tle import TLE
from infrastructure.utils.tle_parser import TLEParser


class CelesTrakTLEService(TLEServiceInterface):

    BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"

    def fetch_tle(self, norad_id: str) -> Optional[TLE]:
        try:
            params = {
                "CATNR": norad_id,
                "FORMAT": "2LE"
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            lines = response.text.strip().split('\n')
            lines = [line.strip() for line in lines if line.strip()]

            if len(lines) >= 2:
                line1 = lines[0]
                line2 = lines[1]

                if TLEParser.validate_tle(line1, line2):
                    return TLEParser.parse_tle(line1, line2)

            return None

        except requests.RequestException as e:
            print(f"Error fetching TLE from CelesTrak: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching TLE: {e}")
            return None
