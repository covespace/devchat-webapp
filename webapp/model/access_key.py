from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from webapp.utils import generate_access_key, hash_access_key
from .database import Base


class AccessKey(Base):
    """
    AccessKey model

    Attributes:
        id (int): Unique auto-increment Biginteger identifier for the key
        name (str): Name of the key
        key_hash (str): Hash of the key for storage and comparison
        prefix (str): Prefix for the key based on the target service region
        create_time (datetime): Time when the key was created
        revoke_time (datetime): Time when the key was revoked
        user_id (int): Foreign key for the user associated with the key
        organization_id (int): Foreign key for the organization associated with the key
    """
    __tablename__ = 'access_keys'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    key_hash = Column(String, nullable=False)
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
        key = generate_access_key(self.organization_id)
        self.key_hash = hash_access_key(key)
        self.prefix = f"dc-{region}-" + key[:4]

    def __repr__(self):
        return f"<AccessKey(id={self.id}, name='{self.name}', " \
               f"key_hash='{self.key_hash}', prefix='{self.prefix}', " \
               f"create_time='{self.create_time}', revoke_time='{self.revoke_time}', " \
               f"user_id={self.user_id}, organization_id={self.organization_id})>"
