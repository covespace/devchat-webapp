"""
utils.py contains utility functions that are used throughout the webapp.
"""
from datetime import datetime
import hashlib
import os
import uuid
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


def generate_access_key(organization_id: str) -> str:
    # Load the RSA private key from environment variables
    private_key = os.environ['JWT_PRIVATE_KEY']
    payload = {
        'organization_id': organization_id,
        'jti': str(uuid.uuid4())  # Add a unique identifier (UUID) to the payload
    }
    key = jwt.encode(payload, private_key, algorithm='RS256')
    return key


def hash_access_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def verify_access_key(key: str) -> str:
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
               template_id: str, template_data: dict):
    from_email = Email(from_email, from_name)
    to_email = To(to_email)
    mail = Mail(from_email, to_email)

    # Set the transactional template ID
    mail.template_id = template_id

    # Set the dynamic template data
    mail.dynamic_template_data = template_data

    try:
        client = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
        response = client.send(mail)
        print("Email sent successfully!")
        print("Status code:", response.status_code)
    except Exception as exc:
        print("Error sending email:", exc)
