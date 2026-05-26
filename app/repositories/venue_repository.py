"""Repository for managing venues in the Couchbase database."""
import app.config.config as config
from app.domain.models import Venue


class VenueRepository:
    """Repository for managing venues in the Couchbase database."""
    def __init__(self, db_service):
        self.collection = db_service.get_collection(config.DB_BUCKET, config.VENUE_COLLECTION)

    def upsert(self, venue: Venue):
        """Insert a new venue document or update an existing one.
        """

        categories = [
            category.model_dump(exclude_none=True)
            for category in venue.category]

        self.collection.upsert(
            f"venue::{venue.id}",
            {
                "id": venue.id,
                "name": venue.name,
                "category": categories,
                "location": venue.location.model_dump(exclude_none=True),
                "country": venue.country.model_dump(exclude_none=True)
            }
        )
