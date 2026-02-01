from typing import Optional
from dataclasses import dataclass


@dataclass
class TLE:
    line1: str
    line2: str
    norad_id: Optional[str] = None
    epoch: Optional[str] = None
    
    def __post_init__(self):
        if len(self.line1) != 69 or len(self.line2) != 69:
            raise ValueError("TLE lines must be exactly 69 characters")
        
        if self.norad_id is None:
            self.norad_id = self.line1[2:7].strip()
    
    def to_dict(self) -> dict:
        """Convert TLE to dictionary for JSON serialization."""
        return {
            "line1": self.line1,
            "line2": self.line2,
            "norad_id": self.norad_id,
            "epoch": self.epoch
        }
