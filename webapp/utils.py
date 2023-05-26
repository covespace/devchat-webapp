"""
utils.py contains utility functions that are used throughout the webapp.
"""
import json
from datetime import datetime
import hashlib
import logging
import os
import re
import uuid

import boto3
import jwt
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To


def generate_uuid(name: str) -> str:
    # Define a namespace for DevChat
    namespace = uuid.UUID('53835ae0-1173-3b91-34e6-ebcf3983edde')
    # Generate a UUID based on the name
    dev_uuid = uuid.uuid5(namespace, name)
    return str(dev_uuid)


def generate_access_key(organization_id: str, region: str) -> str:
    if not region:
        region = 'any'
    if not re.match(r'^[a-z0-9]{2,4}$', region):
        raise ValueError("Invalid region")

    # Load the RSA private key from environment variables
    private_key = os.environ['JWT_PRIVATE_KEY']
    payload = {
        'organization_id': organization_id,
        'jti': str(uuid.uuid4())  # Add a unique identifier (UUID) to the payload
    }
    key = jwt.encode(payload, private_key, algorithm='RS256')
    return f'dc-{region}-' + key


def hash_access_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def verify_access_key(key: str) -> str:
    pattern = r'^dc-[a-z0-9]{2,4}-'
    if not re.match(pattern, key):
        raise ValueError("Invalid access key prefix")
    key = re.sub(pattern, '', key)

    # Load the RSA public key from environment variables
    public_key = os.environ['JWT_PUBLIC_KEY']
    try:
        payload = jwt.decode(key, public_key, algorithms=['RS256'])
        return payload['organization_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def now(db: Session) -> datetime:
    return db.query(func.now()).scalar()  # pylint: disable=E1102


def send_email(from_email: str, from_name: str, to_email: str,
               template_id: str, template_data: dict) -> int:
    from_email = Email(from_email, from_name)
    to_email = To(to_email)
    mail = Mail(from_email, to_email)

    # Set the transactional template ID
    mail.template_id = template_id

    # Set the dynamic template data
    mail.dynamic_template_data = template_data

    client = SendGridAPIClient(get_sendgrid_api_key())
    response = client.send(mail)
    return response.status_code


def get_logger(name: str = None) -> logging.Logger:
    logger = logging.getLogger(name)

    # Default to 'INFO' if 'LOG_LEVEL' env var is not set
    log_level_str = os.getenv('LOG_LEVEL')
    if not log_level_str:
        log_level = logging.INFO
    else:
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    logger.setLevel(log_level)

    # Create console handler with a higher log level
    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(handler)

    logger.info("Log level set to %s (env: %s)", log_level, log_level_str)
    return logger


def get_jwt_public_key() -> str:
    """
    Get the RSA public key from environment variables.
    """
    return get_secret_from_aws_secrets_manager('JWT_PUBLIC_KEY', 'JWT_PUBLIC_KEY')


def get_jwt_private_key() -> str:
    """
    Get the RSA private key from environment variables.
    """
    return get_secret_from_aws_secrets_manager('JWT_PRIVATE_KEY', 'JWT_PRIVATE_KEY')


def get_sendgrid_api_key() -> str:
    """
    Get the SendGrid API key from environment variables.
    """
    if 'SENDGRID_API_KEY' in os.environ:
        return os.environ['SENDGRID_API_KEY']
    return get_secret_from_aws_secrets_manager('SENDGRID', 'API_KEY')


def get_secret_from_aws_secrets_manager(secret_name: str, key_name: str) -> str:
    """
    Get a secret from AWS Secrets Manager.
    """

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
    # Assuming the secret is a string, we parse it as a JSON object
    secret_dict = json.loads(get_secret_value_response['SecretString'])

    if key_name not in secret_dict:
        raise ValueError("Unable to get the secret from AWS Secrets Manager")
    return secret_dict[key_name]
