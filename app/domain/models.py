from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum
from typing import List


class Country(BaseModel):
    code: str = Field(min_length=2, max_length=2)
    name: str


class Checkin(BaseModel):
    timestamp: datetime
    offset: int
    venueId: str


class User(BaseModel):
    id: int
    name: str
    surname: str
    birthDate: date
    country: Country
    checkins: List[Checkin]


class FriendshipStatus(Enum):
    ACCEPTED = "accepted"
    PENDING = "pending"
    DENIED = "denied"
    BLOCKED = "blocked"


class Friendship(BaseModel):
    user1: int
    user2: int
    status: FriendshipStatus
    friendSince: datetime


class VenueCategory(BaseModel):
    id: str
    name: str


class Venue(BaseModel):
    id: str
    name: str
    category: VenueCategory
    latitude: float
    longitude: float
    country: Country
    majorId: int
