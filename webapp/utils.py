"""
utils.py contains utility functions that are used throughout the webapp.
"""
from datetime import datetime
import hashlib
import logging
import os
import random
import re
import time
import uuid

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


def is_valid_account_name(user_name):
    name_regex = r'^[a-zA-Z0-9](?:[a-zA-Z0-9]|[-_](?=[a-zA-Z0-9])){0,37}[a-zA-Z0-9]$'
    return re.match(name_regex, user_name) is not None


def generate_uuid(name: str) -> str:
    # Define a namespace for DevChat
    namespace = uuid.UUID('53835ae0-1173-3b91-34e6-ebcf3983edde')
    # Generate a UUID based on the name
    dev_uuid = uuid.uuid5(namespace, name)
    return str(dev_uuid)


def generate_access_key(org_id: int) -> str:
    if not org_id:
        raise ValueError("Invalid organization ID")
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


def send_email(from_address: str, from_name: str, to_address: str,
               template_id: str, template_data: dict) -> int:
    from_email = Email(from_address, from_name)
    to_email = To(to_address)
    mail = Mail(from_email, to_email)

    # Set the transactional template ID
    mail.template_id = template_id

    # Set the dynamic template data
    mail.dynamic_template_data = template_data

    client = SendGridAPIClient(_get_sendgrid_api_key())
    response = client.send(mail)
    logger.info("Sent email of template %s to %s with status code %s",
                template_id, to_address, response.status_code)
    return response.status_code


def _get_jwt_secret_key() -> str:
    secret_key = os.getenv('JWT_SECRET_KEY')
    if secret_key is None:
        raise ValueError("JWT_SECRET_KEY environment variable is not set")
    return secret_key


def _get_sendgrid_api_key() -> str:
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    if sendgrid_api_key is None:
        raise ValueError("SENDGRID_API_KEY environment variable is not set")
    return sendgrid_api_key
