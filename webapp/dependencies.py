import os
from sqlalchemy.orm import Session
from webapp.model.database import Database
from webapp.utils import get_logger, get_secrets_from_aws


logger = get_logger(__name__)


def get_database_url() -> str:
    """
    Get the database URL from environment variable or AWS Secrets Manager.
    Returns:
        str: The database URL.
    """

    # Try to get the database URL from environment variable
    db_url = os.getenv("DATABASE_URL")
    if db_url is not None:
        logger.info("Got database URL from environment variable")
        return db_url

    # If the environment variable is not set, get the database URL from AWS Secrets Manager
    db_name = "devchat"
    secrets = get_secrets_from_aws("pg-1")

    db_url = f"postgresql://{secrets['username']}:{secrets['password']}@" \
             f"{secrets['host']}:{secrets['port']}/{db_name}"

    logger.info("Got database URL from AWS Secrets Manager")
    return db_url


database = Database(get_database_url())


def get_db() -> Session:
    with database.get_session() as db:
        yield db
