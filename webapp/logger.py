import logging
import os


def setup_logger():
    """Set up root logger"""

    # Default to 'INFO' if 'LOG_LEVEL' env var is not set
    log_level_str = os.getenv('LOG_LEVEL', 'INFO')
    # Default to INFO if the specified level is invalid
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(ch)
