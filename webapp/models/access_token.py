"""
access_token.py contains the AccessToken model.
"""
import datetime
import hashlib
import os
import jwt
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from webapp.database import Base


# Load the RSA private and public keys from environment variables
PUBLIC_KEY = os.environ['JWT_PUBLIC_KEY']
PRIVATE_KEY = os.environ['JWT_PRIVATE_KEY']


class AccessToken(Base):
    """
    AppToken model

    Attributes:
        id (int): Unique auto-increment integer identifier for the token
        name (str): Name of the token
        token_hash (str): Hash of the token for storage and comparison
        prefix (str): Prefix for the token based on the target service location
        create_time (datetime): Time when the token was created
        revoke_time (datetime): Time when the token was revoked
        user_id (int): Foreign key for the user associated with the token
        organization_id (int): Foreign key for the organization associated with the token
    """
    __tablename__ = 'access_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    token_hash = Column(String, nullable=False)
    prefix = Column(String, nullable=False)
    create_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    revoke_time = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'))

    user = relationship("User", back_populates="app_tokens")
    organization = relationship("Organization", back_populates="app_tokens")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        token = self.generate_token(self.user_id, self.organization_id)
        self.token_hash = self.hash_token(token)
        self.prefix = f"dc-{kwargs.get('location', 'xyz')}-" + token[:4]

    @classmethod
    def generate_token(cls, user_id, organization_id):
        payload = {
            'user_id': user_id,
            'organization_id': organization_id
        }
        token = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256')
        return token

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def verify_token(cls, token):
        try:
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=['RS256'])
            return payload['user_id'], payload['organization_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def __repr__(self):
        return f"<AccessToken(id={self.id}, name='{self.name}', \
                token='{self.token}', prefix='{self.prefix}', \
                create_time='{self.create_time}', revoke_time='{self.revoke_time}', \
                user_id={self.user_id}, organization_id={self.organization_id})>"
