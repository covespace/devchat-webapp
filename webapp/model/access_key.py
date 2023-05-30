from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from webapp.utils import hash_access_key
from .database import Base


class AccessKey(Base):
    """
    AccessKey model

    Attributes:
        id (int): Unique auto-increment Biginteger identifier for the key
        name (str): Name of the key
        key_hash (str): Hash of the key for storage and comparison
        thumbnail (str): Thumbnail of the key as a hint for the user
        create_time (datetime): Time when the key was created
        revoke_time (datetime): Time when the key was revoked
        user_id (int): Foreign key for the user associated with the key
        organization_id (int): Foreign key for the organization associated with the key
    """
    __tablename__ = 'access_keys'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    key_hash = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    create_time = Column(DateTime(timezone=True), nullable=False,
                         default=func.now())  # pylint: disable=E1102
    revoke_time = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    organization_id = Column(BigInteger, ForeignKey('organizations.id'))

    user = relationship("User", back_populates="access_keys")
    organization = relationship("Organization", back_populates="access_keys")

    def __init__(self, key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_hash = hash_access_key(key)
        self.thumbnail = key[:7] + '...' + key[-7:]

    def __repr__(self):
        return f"<AccessKey(id={self.id}, name='{self.name}', " \
               f"key_hash='{self.key_hash}', thumbnail='{self.thumbnail}', " \
               f"create_time='{self.create_time}', revoke_time='{self.revoke_time}', " \
               f"user_id={self.user_id}, organization_id={self.organization_id})>"
