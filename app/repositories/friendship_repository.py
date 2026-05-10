"""Repository for managing friendships in the Couchbase database."""
import app.config as config
from app.domain.models import Friendship
from app.services.db_service import db_service


class FriendshipRepository:
    """Repository for managing friendships in the Couchbase database."""
    def __init__(self):
        self.collection = db_service.get_collection(config.DB_BUCKET, config.FRIENDSHIP_COLLECTION)

    def upsert(self, friendship: Friendship):
        """Insert a new friendship document or update an existing one.
        """
        self.collection.upsert(
            f"friendship::{friendship.user1}::{friendship.user2}",
            {
                "user1": friendship.user1,
                "user2": friendship.user2,
                "status": friendship.status.value,
                "friendSince": friendship.friendSince.isoformat()
            }
        )
