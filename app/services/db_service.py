"""Service for managing the connection to the Couchbase database."""
import app.config.config as config
import time
from couchbase.cluster import Cluster, timedelta
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import BucketNotFoundException, CouchbaseException
from couchbase.management.buckets import CreateBucketSettings
from couchbase.management.collections import CollectionSpec
import logging

logger = logging.getLogger(__name__)


class CouchbaseService:
    """Service for managing the connection to the Couchbase database."""

    def __init__(self):
        max_retries = 10
        for i in range(max_retries):
            if i == 0:
                logger.info("Connecting to Couchbase cluster...")
            else:
                logger.info(
                    "Attempting to connect to Couchbase cluster... Attempt %d of %d...",
                    i + 1, max_retries)

            try:
                self.cluster = Cluster(
                    config.DB_HOST,
                    ClusterOptions(
                        PasswordAuthenticator(
                            config.DB_USER, config.DB_PASSWORD),
                            enable_metrics=False
                    )
                )

                self.cluster.wait_until_ready(timedelta(seconds=30))

                logger.info("Connected!")
                break
            except CouchbaseException:
                if max_retries - 1 == i:
                    logger.error("Failed to connect to Couchbase cluster")
                    raise

                logger.warning("Connection failed, retrying in 10 seconds...")
                time.sleep(10)

    def close(self):
        """Close the connection to the Couchbase cluster."""
        logger.info("Closing Couchbase connection")
        self.cluster.close()

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
            time.sleep(2)

        collection = bucket.collection(collection_name)

        return collection

    def get_cluster(self):
        """Get the Couchbase cluster instance."""
        return self.cluster

    def execute_query(self, query):
        """Execute a N1QL query against the Couchbase cluster."""
        logger.debug("Executing query: %s", query)
        return self.cluster.query(query, options=QueryOptions(metrics=False)).execute()

    def create_secondary_index(self, collection_name, index_name, fields):
        """ Create a secondary index on the specified fields for the given collection. """
        query = f"""
        CREATE INDEX `{index_name}`
        ON `{config.DB_BUCKET}`.`{config.DB_SCOPE}`.`{collection_name}`
        ({','.join(fields)}) WITH {{"defer_build": true}};
        """
        self.execute_query(query)
