""" Query Manager for handling the execution of the project queries. """
import app.config.config as config
from app.config.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)

class QueryManager:
    """Manager for handling the execution of the project queries."""

    def __init__(self, db_service):
        self.db_service = db_service

        setup_logging()

    def execute_q1(self):
        """Execute Q1 query."""
        query = f"SELECT c.* \
                FROM `{config.DB_BUCKET}`.`{config.DB_SCOPE}`.`{config.CHECKIN_COLLECTION}` c \
                WHERE c.userId = 1000006 \
                AND c.timestamp >= \"2012-05-01T00:00:00Z\" \
                AND c.timestamp < \"2012-06-01T00:00:00Z\" \
                ORDER BY c.timestamp;"

        logger.info("Executing query Q1...")
        result = self.db_service.execute_query(query)
        return result

    def execute_q2(self):
        """Execute Q2 query."""
        query = f"SELECT v.* \
                FROM ( \
                    SELECT c.venue.id as venueId \
                    FROM `{config.DB_BUCKET}`.`{config.DB_SCOPE}`.`{config.CHECKIN_COLLECTION}` c \
                    WHERE c.timestamp >= \"2012-05-19T00:00:00Z\" \
                    AND c.timestamp < \"2012-05-20T00:00:00Z\" \
                    GROUP BY c.venue.id \
                    HAVING COUNT(DISTINCT c.userId) > 200 \
                ) AS popular_venues \
                JOIN `{config.DB_BUCKET}`.`{config.DB_SCOPE}`.`{config.VENUE_COLLECTION}` v \
                    ON KEYS \"venue::\" || popular_venues.venueId;"

        logger.info("Executing query Q2...")
        result = self.db_service.execute_query(query)
        return result

    def execute_q3(self):
        """Execute Q3 query."""
        query = f"SELECT c1.*, c2.* \
                FROM `{config.DB_BUCKET}`.`{config.DB_SCOPE}`.`{config.USER_COLLECTION}` u \
                USE KEYS \"user::1000006\" \
                UNNEST u.friends f \
                JOIN `{config.DB_BUCKET}`.`{config.DB_SCOPE}`.`{config.CHECKIN_COLLECTION}` c1 \
                    ON c1.userId = u.id \
                JOIN `{config.DB_BUCKET}`.`{config.DB_SCOPE}`.`{config.CHECKIN_COLLECTION}` c2 \
                    ON c2.userId = f.friendId \
                WHERE c1.venue.id = c2.venue.id \
                AND c2.timestamp >= DATE_ADD_STR(c1.timestamp, -10, \"minute\") \
                AND c2.timestamp < DATE_ADD_STR(c1.timestamp, 10, \"minute\")"

        logger.info("Executing query Q3...")
        result = self.db_service.execute_query(query)
        return result
