"""Repository for managing check-ins in the Couchbase database."""
import app.config as config
from app.domain.models import Checkin


class CheckinRepository:
    """Repository for managing check-ins in the Couchbase database."""
    def __init__(self, db_service):
        self.collection = db_service.get_collection(config.DB_BUCKET, config.CHECKIN_COLLECTION)

    def upsert(self, checkin: Checkin):
        """Insert a new check-in document or update an existing one.
        """
        self.collection.upsert(
            f"checkin::{checkin.userId}::{checkin.venue.id}::{checkin.utcTimestamp.isoformat()}",
            {
                "id": checkin.id,
                "userId": checkin.userId,
                "venue": checkin.venue.model_dump(),
                "timestamp": checkin.utcTimestamp.isoformat(),
                "offset": checkin.offset,
                "utcTime": checkin.utcTimeStr
            }
        )
