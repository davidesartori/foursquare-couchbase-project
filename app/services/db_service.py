"""Service for managing the connection to the Couchbase database."""
import app.config as config
import time
from couchbase.cluster import Cluster, timedelta
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import BucketNotFoundException
from couchbase.management.buckets import CreateBucketSettings
from couchbase.management.collections import CollectionSpec


class CouchbaseService:
    """Service for managing the connection to the Couchbase database."""

    def __init__(self):
        self.cluster = Cluster(
            config.DB_HOST,
            ClusterOptions(
                PasswordAuthenticator(config.DB_USER, config.DB_PASSWORD)
            )
        )

        self.cluster.wait_until_ready(timedelta(seconds=5))


    def get_bucket(self, bucket_name):
        """Get a reference to a Couchbase bucket, creating it if it doesn't exist."""
        try:
            bucket = self.cluster.bucket(bucket_name)
        except BucketNotFoundException:
            bucket_manager = self.cluster.buckets()

            bucket_manager.create_bucket(
                CreateBucketSettings(
                    name=bucket_name,
                    bucket_type="couchbase",
                    ram_quota_mb=config.DB_BUCKET_RAM_QUOTA_MB
                )
            )

            time.sleep(5)

            bucket = self.cluster.bucket(bucket_name)

        return bucket


    def get_collection(self, bucket_name, collection_name):
        """Get a reference to a Couchbase collection, creating it if it doesn't exist."""
        bucket = self.get_bucket(bucket_name)
        collection_manager = bucket.collections()
        existing_collections = [c.name for scope in collection_manager.get_all_scopes()
                                for c in scope.collections]

        if collection_name not in existing_collections:
            collection_manager.create_collection(
                CollectionSpec(collection_name, scope_name="_default"))
            time.sleep(1)

        collection = bucket.collection(collection_name)

        return collection


# single shared instance
db_service = CouchbaseService()
