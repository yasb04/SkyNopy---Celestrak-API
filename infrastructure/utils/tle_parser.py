from __future__ import annotations
from datetime import datetime, timedelta, timezone
from domain.models.tle import TLE


class TLEParser:
    @staticmethod
    def parse_tle(line1: str, line2: str) -> TLE:

        if not TLEParser.validate_tle(line1, line2):
            raise ValueError("Invalid TLE format")

        year_str = line1[18:20].strip()
        day_of_year_str = line1[20:23].strip()
        fractional_day_str = line1[23:32].strip()

        epoch_dt = TLEParser._parse_epoch(year_str, day_of_year_str, fractional_day_str)

        if epoch_dt.tzinfo is None:
            epoch_dt = epoch_dt.replace(tzinfo=timezone.utc)
        epoch_iso = epoch_dt.isoformat().replace("+00:00", "Z")

        return TLE(line1=line1, line2=line2, epoch=epoch_iso)

    @staticmethod
    def _parse_epoch(year_str: str, day_of_year_str: str, fractional_day_str: str) -> datetime:
        try:
            year_int = int(year_str)
        except ValueError:
            raise ValueError("Invalid TLE format: year must be numeric")
        #57–99 → 1957–1999, 00–56 → 2000–2056
        if year_int >= 57:
            year = 1900 + year_int
        else:
            year = 2000 + year_int

        try:
            day_of_year = int(day_of_year_str)
        except ValueError:
            raise ValueError("Invalid TLE format: day of year must be numeric")
        if fractional_day_str.startswith("."):
            fractional_day = float(f"0{fractional_day_str}")
        else:
            fractional_day = float(f"0.{fractional_day_str}")

        base_date = datetime(year, 1, 1)
        target_date = base_date + timedelta(days=day_of_year - 1)
        seconds_in_day = fractional_day * 86400
        target_date = target_date + timedelta(seconds=seconds_in_day)

        return target_date


    @staticmethod
    def validate_tle(line1: str, line2: str) -> bool:
        if not line1 or not line2:
            return False

        if len(line1) != 69 or len(line2) != 69:
            return False

        if not line1.startswith("1 ") or not line2.startswith("2 "):
            return False

        norad_id_1 = line1[2:7].strip()
        norad_id_2 = line2[2:7].strip()

        if norad_id_1 != norad_id_2:
            return False

        return True
