"""Repository for managing venues in the Couchbase database."""
import app.config as config
from app.domain.models import Venue
from app.services.db_service import db_service


class VenueRepository:
    """Repository for managing venues in the Couchbase database."""
    def __init__(self):
        self.collection = db_service.get_collection(config.DB_BUCKET, config.VENUE_COLLECTION)

    def upsert(self, venue: Venue):
        """Insert a new venue document or update an existing one.
        """
        self.collection.upsert(
            f"venue::{venue.id}",
            {
                "id": venue.id,
                "name": venue.name,
                "category": venue.category.model_dump(exclude_none=True),
                "latitude": venue.latitude,
                "longitude": venue.longitude,
                "country": venue.country.model_dump(exclude_none=True),
                "majorId": venue.majorId
            }
        )
