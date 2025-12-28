"""Vehicle data model"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Vehicle:
    """Data class representing a Renault vehicle listing"""
    title: str
    price: int
    trim: str
    charge_type: str
    exterior_color: str
    seat_type: str
    packs: str
    location: str
    url: str
    photo_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
