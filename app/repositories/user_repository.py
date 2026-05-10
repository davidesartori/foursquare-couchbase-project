"""Repository for managing users in the Couchbase database."""
import app.config as config
from app.domain.models import User
from app.services.db_service import db_service


class UserRepository:
    """Repository for managing users in the Couchbase database."""
    def __init__(self):
        self.collection = db_service.get_collection(config.DB_BUCKET, config.USER_COLLECTION)

    def upsert(self, user: User):
        """Insert a new user document or update an existing one.
        """
        checkins = []

        for checkin in user.checkins:
            checkins.append({
                "timestamp": checkin.timestamp.isoformat(),
                "offset": checkin.offset,
                "venueId": checkin.venueId,
                "utcTime": checkin.utcTime
            })

        self.collection.upsert(
            f"user::{user.id}",
            {
                "id": user.id,
                "name": "",
                "surname": "",
                "birthDate": str(user.birthDate),
                "country": user.country.model_dump(exclude_none=True),
                "checkins": checkins
            }
        )
