import os
import logging

import boto3
from sqlalchemy.orm import Session

from webapp.model.database import Database


logger = logging.getLogger(__name__)


def get_db() -> Session:
    with database.get_session() as db:
        yield db


def get_database_url() -> str:
    """
    Get the database URL from environment variable or AWS Secrets Manager.
    Returns:
        str: The database URL.
    Raises:
        Exception: If the database URL cannot be obtained.
    """

    # Try to get the database URL from environment variable
    db_url = os.getenv("DATABASE_URL")

    if db_url is not None:
        logger.info("Got database URL from environment variable")
        return db_url

    # If the environment variable is not set, get the database URL from AWS Secrets Manager
    secret_name = "pg-1"
    region_name = "ap-southeast-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as exc:
        # Raise an exception if unable to get the secret
        raise ValueError("Unable to get the secret from AWS Secrets Manager") from exc

    # Decrypts secret using the associated KMS key.
    # Assuming the secret is a string
    db_url = get_secret_value_response['SecretString']

    if db_url is None:
        raise ValueError("Unable to get the database URL")

    logger.info("Got database URL from AWS Secrets Manager")
    return db_url


database = Database(get_database_url())
