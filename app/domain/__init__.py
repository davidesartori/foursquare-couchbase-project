"""Domain module for defining the core data models of the application."""
# models/__init__.py
from .models import Country
from .models import Checkin
from .models import User
from .models import FriendshipStatus
from .models import Friendship
from .models import VenueCategory
from .models import Venue

__all__ = [
    "Country",
    "Checkin",
    "User",
    "FriendshipStatus",
    "Friendship",
    "VenueCategory",
    "Venue"
]
