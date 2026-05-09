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


class Checkin(BaseModel):
    """Represents a check-in event by a user at a venue."""
    timestamp: datetime
    offset: int
    venueId: str
    utcTime: str | None


class User(BaseModel):
    """Represents a user in the system."""
    id: int
    name: str
    surname: str
    birthDate: date
    country: Country
    checkins: List[Checkin]


class FriendshipStatus(Enum):
    """Represents the status of a friendship between two users."""
    ACCEPTED = "accepted"
    PENDING = "pending"
    DENIED = "denied"
    BLOCKED = "blocked"


class Friendship(BaseModel):
    """Represents a friendship between two users."""
    user1: int
    user2: int
    status: FriendshipStatus
    friendSince: datetime


class VenueCategory(BaseModel):
    """Represents a category of a venue."""
    id: str
    name: str


class Venue(BaseModel):
    """Represents a venue where users can check in."""
    id: str
    name: str
    category: VenueCategory
    latitude: float
    longitude: float
    country: Country
    majorId: int
