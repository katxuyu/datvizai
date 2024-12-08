import logging
from logging.handlers import TimedRotatingFileHandler
import uuid
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the log directory exists

def setup_logging():
    """
    Configures logging for the application, with log rotation every hour.
    """
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.INFO)

    # Create a timed rotating file handler
    handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, 'app.log'),
        when='h',  # Rotate every hour
        interval=1,
        backupCount=24,  # Keep logs for 24 hours
        encoding='utf-8'
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s [Request ID: %(request_id)s]'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

# Attach unique request ID to log messages
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = uuid.uuid4().hex  # Add a unique request ID to every log message
        return True

# Configure the logger globally
logger = setup_logging()
logger.addFilter(RequestIDFilter())
