import os

import boto3
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session

from webapp.model.database import Database

database = None


def get_database():
    """
    Get the database instance.
    :return: the database instance
    """
    global database
    if database is None:
        db_url = get_database_url()
        database = Database(db_url)
    return database


def init_tables():
    """
    Initialize the database tables.
    """
    db = get_database()
    return db.create_tables()


def get_db() -> Session:
    global database
    if database is None:
        db_url = get_database_url()
        database = Database(db_url)
    with database.get_session() as session:
        yield session


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
    except ClientError as e:
        # Raise an exception if unable to get the secret
        raise Exception("Unable to get the secret from AWS Secrets Manager") from e

    # Decrypts secret using the associated KMS key.
    # Assuming the secret is a string
    db_url = get_secret_value_response['SecretString']

    if db_url is None:
        raise Exception("Unable to get the database URL")

    return db_url
