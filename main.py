""" Foursquare Couchbase Project - App orchestrator """

from app.scripts.db_init import main as db_init
from app.scripts.run_queries import main as run_queries
from app.config.logging_config import setup_logging
import logging
import sys

logger = logging.getLogger(__name__)


def main():
    """ Main function to launch the couchbase project """

    setup_logging()

    try:
        db_init()
        run_queries()
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
