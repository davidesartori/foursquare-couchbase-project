"""Defines the data models used in the application."""
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum
from typing import List


class Country(BaseModel):
    """Represents a country with its code and name.
    """
    code: str = Field(min_length=2, max_length=2)
    name: str


class VenueCategory(BaseModel):
    """Represents a category of a venue."""
    id: str
    name: str


class Location(BaseModel):
    """Represents a geographical location using GeoJSON format."""
    type: str = "Point"
    coordinates: list[float]

    @classmethod
    def get_coordinates_list(cls, latitude: float, longitude: float) -> "Location":
        """Helper method to create a Location instance from latitude and longitude."""
        return cls(coordinates=[longitude, latitude])


class Venue(BaseModel):
    """Represents a venue where users can check in."""
    id: str
    name: str
    category: VenueCategory
    location: Location
    country: Country


class Checkin(BaseModel):
    """Represents a check-in event by a user at a venue."""
    id: int
    userId: int
    venue: Venue | None
    utcTimestamp: datetime
    offset: int
    utcTimeStr: str | None = None


class FriendshipStatus(Enum):
    """Represents the status of a friendship between two users."""
    ACCEPTED = "accepted"
    PENDING = "pending"
    DENIED = "denied"
    BLOCKED = "blocked"


class Friendship(BaseModel):
    """Represents a friendship between two users."""
    friendId: int
    status: FriendshipStatus
    friendSince: datetime


class User(BaseModel):
    """Represents a user in the system."""
    id: int
    name: str
    surname: str
    birthDate: date | None
    country: Country
    friends: List[Friendship]
