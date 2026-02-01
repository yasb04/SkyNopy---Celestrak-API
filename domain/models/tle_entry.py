from datetime import datetime, timezone
from dataclasses import dataclass, field
from domain.models.tle import TLE


@dataclass
class TLEEntry:
    tle: TLE
    source: str
    fetched_at: datetime
    stored_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> dict:
        fetched_at_dt = self.fetched_at
        if fetched_at_dt.tzinfo is None:
            fetched_at_dt = fetched_at_dt.replace(tzinfo=timezone.utc)
        
        stored_at_dt = self.stored_at
        if stored_at_dt.tzinfo is None:
            stored_at_dt = stored_at_dt.replace(tzinfo=timezone.utc)
        
        return {
            "line1": self.tle.line1,
            "line2": self.tle.line2,
            "epoch": self.tle.epoch,
            "source": self.source,
            "fetched_at": fetched_at_dt.isoformat(),
            "stored_at": stored_at_dt.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TLEEntry":
        tle = TLE(
            line1=data["line1"],
            line2=data["line2"],
            epoch=data.get("epoch")
        )
        
        fetched_at_str = data["fetched_at"]
        if fetched_at_str.endswith("Z"):
            fetched_at_str = fetched_at_str[:-1] + "+00:00"
        fetched_at = datetime.fromisoformat(fetched_at_str)
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        
        stored_at_str = data["stored_at"]
        if stored_at_str.endswith("Z"):
            stored_at_str = stored_at_str[:-1] + "+00:00"
        stored_at = datetime.fromisoformat(stored_at_str)
        if stored_at.tzinfo is None:
            stored_at = stored_at.replace(tzinfo=timezone.utc)
        
        return cls(
            tle=tle,
            source=data["source"],
            fetched_at=fetched_at,
            stored_at=stored_at
        )
