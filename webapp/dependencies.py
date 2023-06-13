import os
from sqlalchemy.orm import Session
from webapp.model.database import Database
from webapp.utils import get_logger

logger = get_logger(__name__)


def get_database_url() -> str:
    """
    Get the database URL from environment variable or AWS Secrets Manager.
    Returns:
        str: The database URL.
    """

    # Try to get the database URL from environment variable
    db_url = os.getenv("DATABASE_URL")
    if db_url is None:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return db_url


database = Database(get_database_url())


def get_db() -> Session:
    with database.get_session() as db:
        yield db
