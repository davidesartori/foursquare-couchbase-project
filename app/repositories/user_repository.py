"""Repository for managing users in the Couchbase database."""
import app.config.config as config
from app.domain.models import User
from app.config.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for managing users in the Couchbase database."""

    def __init__(self, db_service):
        self.db_service = db_service
        self.collection = db_service.get_collection(
            config.DB_BUCKET, config.USER_COLLECTION)

        setup_logging()


    def upsert(self, user: User):
        """Insert a new user document or update an existing one.
        """

        friends = []

        for friend in user.friends:
            friends.append({
                "friendId": friend.friendId,
                "status": friend.status.value,
                "friendSince": friend.friendSince.isoformat()
            })

        self.collection.upsert(
            f"user::{user.id}",
            {
                "id": user.id,
                "name": "",
                "surname": "",
                "birthDate": str(user.birthDate),
                "country": user.country.model_dump(exclude_none=True),
                "friends": friends,
            }
        )
