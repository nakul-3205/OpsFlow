import psycopg2
from config.settings import settings
from logger_service.logger import setup_logger
from core.error_handler import APIException
import time

logger = setup_logger()

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

for attempt in range(1, MAX_RETRIES + 1):
    try:
        logger.info(f"Connecting to the database, attempt {attempt}")
        conn = psycopg2.connect(settings.database_url)
        logger.info("Database connection successful")
        break
    except psycopg2.OperationalError as e:
        logger.warning(f"Database connection attempt {attempt} failed: {e}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
        else:
            logger.error("All database connection attempts failed")
            raise APIException(
                "Database connection error",
                status_code=500,
                details={"error": str(e)}
            )
