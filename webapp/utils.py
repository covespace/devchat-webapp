"""
utils.py contains utility functions that are used throughout the webapp.
"""
from datetime import datetime, timezone
import hashlib
import os
from typing import Tuple
import uuid
import jwt


def generate_uuid(name: str) -> str:
    # Define a namespace for DevChat
    namespace = uuid.UUID('53835ae0-1173-3b91-34e6-ebcf3983edde')
    # Generate a UUID based on the name
    dev_uuid = uuid.uuid5(namespace, name)
    return str(dev_uuid)


def generate_access_token(user_id: str, organization_id: str) -> str:
    # Load the RSA private key from environment variables
    private_key = os.environ['JWT_PRIVATE_KEY']
    payload = {
        'user_id': user_id,
        'organization_id': organization_id,
        'jti': str(uuid.uuid4())  # Add a unique identifier (UUID) to the payload
    }
    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token


def hash_access_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_access_token(token: str) -> Tuple[str, str]:
    # Load the RSA public key from environment variables
    public_key = os.environ['JWT_PUBLIC_KEY']
    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload['user_id'], payload['organization_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def current_time() -> datetime:
    return datetime.now(timezone.utc)
