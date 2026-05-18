"""Index manager for handling database indexes."""
import time
import app.config.config as config
from app.config.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)


class IndexManager:
    """Manager for handling database indexes."""

    def __init__(self, db_service):
        self.db_service = db_service

        setup_logging()

    def create_indexes(self, index_definition):
        """Create the specified indexes."""
        for collection, indexes in index_definition.items():
            for index_name, fields in indexes:
                logger.info("Creating %s index on %s collection if it doesn't exist...",
                            index_name, collection)

                collection_index_created = False

                required_index = self.db_service.execute_query(
                    f"""SELECT * FROM system:indexes WHERE indexes.name = "{index_name}";""")

                if not required_index:
                    self.db_service.create_secondary_index(
                        collection, index_name, fields)
                    collection_index_created = True
                else:
                    logger.info(
                        "Index %s already exists, skipping index creation", index_name)

            if collection_index_created:
                logger.info(
                    "Indexes created for %s collection, building indexes...", collection)
                self.build_indexes(
                    collection, [index_name for index_name, _ in indexes])

        self.wait_for_indexes()

    def build_indexes(self, collection, indexes):
        """Build the specified indexes."""
        logger.info("Building indexes: %s", ", ".join(indexes))
        self.db_service.execute_query(
            f"BUILD INDEX ON `{config.DB_BUCKET}`.`{config.DB_SCOPE}`.`{collection}` \
            ({",".join(indexes)}) USING GSI;")

    def wait_for_indexes(self):
        """Wait for all indexes to be built."""
        logger.info("Waiting for indexes to be built...")
        indexes_ready = False

        while not indexes_ready:
            result = self.db_service.execute_query(
                "SELECT * FROM system:indexes where state != 'online';")

            if not result:
                indexes_ready = True
            else:
                time.sleep(10)
