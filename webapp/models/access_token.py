"""
access_token.py contains the AccessToken model.
"""
import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from webapp.database import Base
from webapp.utils import generate_access_token, hash_access_token


class AccessToken(Base):
    """
    AppToken model

    Attributes:
        id (int): Unique auto-increment integer identifier for the token
        name (str): Name of the token
        token_hash (str): Hash of the token for storage and comparison
        prefix (str): Prefix for the token based on the target service region
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

    user = relationship("User", back_populates="access_tokens")
    organization = relationship("Organization", back_populates="access_tokens")

    def __init__(self, *args, **kwargs):
        region = kwargs.pop('region', 'any')  # Extract the 'region' value and remove it from kwargs
        super().__init__(*args, **kwargs)
        token = generate_access_token(self.user_id, self.organization_id)
        self.token_hash = hash_access_token(token)
        self.prefix = f"dc-{region}-" + token[:4]

    def __repr__(self):
        return f"<AccessToken(id={self.id}, name='{self.name}', \
                token='{self.token}', prefix='{self.prefix}', \
                create_time='{self.create_time}', revoke_time='{self.revoke_time}', \
                user_id={self.user_id}, organization_id={self.organization_id})>"
