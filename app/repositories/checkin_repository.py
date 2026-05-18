"""Repository for managing check-ins in the Couchbase database."""
import app.config.config as config
from app.domain.models import Checkin
from datetime import timezone
from app.config.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)


class CheckinRepository:
    """Repository for managing check-ins in the Couchbase database."""

    def __init__(self, db_service):
        self.db_service = db_service
        self.collection = db_service.get_collection(
            config.DB_BUCKET, config.CHECKIN_COLLECTION)

        setup_logging()


    def upsert(self, checkin: Checkin):
        """Insert a new check-in document or update an existing one.
        """
        self.collection.upsert(
            f"checkin::{checkin.userId}::{checkin.venue.id}::{checkin.utcTimestamp.isoformat()}",
            {
                "id": checkin.id,
                "userId": checkin.userId,
                "venue": checkin.venue.model_dump(),
                "timestamp": checkin.utcTimestamp.astimezone(timezone.utc)
                            .strftime("%Y-%m-%dT%H:%M:%SZ"),
                "offset": checkin.offset,
                "utcTime": checkin.utcTimeStr
            }
        )
