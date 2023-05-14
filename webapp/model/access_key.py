"""
access_token.py contains the AccessKey model.
"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from webapp.utils import generate_access_token, hash_access_token
from .database import Base


class AccessKey(Base):
    """
    AppToken model

    Attributes:
        id (int): Unique auto-increment Biginteger identifier for the token
        name (str): Name of the token
        token_hash (str): Hash of the token for storage and comparison
        prefix (str): Prefix for the token based on the target service region
        create_time (datetime): Time when the token was created
        revoke_time (datetime): Time when the token was revoked
        user_id (int): Foreign key for the user associated with the token
        organization_id (int): Foreign key for the organization associated with the token
    """
    __tablename__ = 'access_keys'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    token_hash = Column(String, nullable=False)
    prefix = Column(String, nullable=False)
    create_time = Column(DateTime(timezone=True), nullable=False,
                         default=func.now())  # pylint: disable=E1102
    revoke_time = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    organization_id = Column(BigInteger, ForeignKey('organizations.id'))

    user = relationship("User", back_populates="access_keys")
    organization = relationship("Organization", back_populates="access_keys")

    def __init__(self, *args, **kwargs):
        region = kwargs.pop('region')  # Extract the 'region' value and remove it from kwargs
        if region is None:
            region = 'any'
        super().__init__(*args, **kwargs)
        token = generate_access_token(self.user_id, self.organization_id)
        self.token_hash = hash_access_token(token)
        self.prefix = f"dc-{region}-" + token[:4]

    def __repr__(self):
        return f"<AccessKey(id={self.id}, name='{self.name}', " \
               f"token_hash='{self.token_hash}', prefix='{self.prefix}', " \
               f"create_time='{self.create_time}', revoke_time='{self.revoke_time}', " \
               f"user_id={self.user_id}, organization_id={self.organization_id})>"
