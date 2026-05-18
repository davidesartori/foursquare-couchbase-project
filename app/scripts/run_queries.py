""" Script to run the project queries. """

import sys
import time
from app.config.logging_config import setup_logging
from app.db.query_manager import QueryManager
from app.services.db_service import CouchbaseService
from couchbase.exceptions import CouchbaseException
import logging
from rich.console import Console


def main():
    """ Main function to run the project queries. """

    setup_logging()
    logger = logging.getLogger(__name__)
    console = Console()

    try:
        db_service = CouchbaseService()
    except CouchbaseException:
        logger.error("Unable to connect to Couchbase cluster")
        sys.exit(1)

    logger.info("Executing queries...")
    query_manager = QueryManager(db_service)

    with console.status("[white]Executing query...[/]",
                        spinner="material", spinner_style="white"):
        start = time.perf_counter()
        query_manager.execute_q1()
        end = time.perf_counter()

    logger.info("Query Q1 executed in %.2f seconds", end - start)

    with console.status("[white]Executing query...[/]",
                        spinner="material", spinner_style="white"):
        start = time.perf_counter()
        query_manager.execute_q2()
        end = time.perf_counter()

    logger.info("Query Q2 executed in %.2f seconds", end - start)

    with console.status("[white]Executing query...[/]",
                        spinner="material", spinner_style="white"):
        start = time.perf_counter()
        query_manager.execute_q3()
        end = time.perf_counter()

    logger.info("Query Q3 executed in %.2f seconds", end - start)

if __name__ == "__main__":
    main()
