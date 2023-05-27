"""
utils.py contains utility functions that are used throughout the webapp.
"""
import json
from datetime import datetime
import hashlib
import logging
import os
import random
import re
import time
import uuid

import boto3
import jwt
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To


def get_logger(name: str = None) -> logging.Logger:
    local_logger = logging.getLogger(name)

    # Default to 'INFO' if 'LOG_LEVEL' env var is not set
    log_level_str = os.getenv('LOG_LEVEL')
    if not log_level_str:
        log_level = logging.INFO
    else:
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    local_logger.setLevel(log_level)

    # Create console handler with a higher log level
    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handlers to the logger
    local_logger.addHandler(handler)

    local_logger.info("Log level set to %s (env: %s)", log_level, log_level_str)
    return local_logger


logger = get_logger(__name__)


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def is_valid_user_name(user_name):
    name_regex = r'^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,37}[a-zA-Z0-9]$'
    return re.match(name_regex, user_name) is not None


def generate_uuid(name: str) -> str:
    # Define a namespace for DevChat
    namespace = uuid.UUID('53835ae0-1173-3b91-34e6-ebcf3983edde')
    # Generate a UUID based on the name
    dev_uuid = uuid.uuid5(namespace, name)
    return str(dev_uuid)


def generate_access_key(org_id: int) -> str:
    # Load the HS256 secret key from environment variables
    secret_key = _get_jwt_secret_key()

    random_bits = random.getrandbits(32)
    timestamp = int(time.time())
    jti = (timestamp << 32) | random_bits

    payload = {
        'org_id': org_id,
        'jti': jti
    }

    key = jwt.encode(payload, secret_key, algorithm='HS256')
    return 'DC.' + key


def verify_access_key(key: str) -> str:
    if not key or not key.startswith('DC.'):
        raise ValueError("Invalid access key prefix")

    # Load the HS256 secret key from environment variables
    secret_key = _get_jwt_secret_key()
    try:
        payload = jwt.decode(key[3:], secret_key, algorithms=['HS256'])
        return payload['org_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_access_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


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

    client = SendGridAPIClient(_get_sendgrid_api_key())
    response = client.send(mail)
    logger.info("Sent email of template %s to %s with status code %s",
                template_id, to_email, response.status_code)
    return response.status_code


def _get_jwt_secret_key() -> str:
    if 'JWT_SECRET_KEY' in os.environ:
        return os.environ['JWT_SECRET_KEY']
    return _get_secret_from_aws_secrets_manager('JWT', 'SECRET_KEY')


def _get_sendgrid_api_key() -> str:
    if 'SENDGRID_API_KEY' in os.environ:
        return os.environ['SENDGRID_API_KEY']
    return _get_secret_from_aws_secrets_manager('SENDGRID', 'API_KEY')


def _get_secret_from_aws_secrets_manager(secret_name: str, key_name: str) -> str:
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
