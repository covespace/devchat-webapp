"""
user.py contains the User model.
"""
import random
import re
from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from webapp.database import Base, Session
from webapp.utils import current_timestamp
from .organization import organization_user


class User(Base):
    """
    User model

    Attributes:
        id (int): Unique integer identifier for the user
        username (str): Unique username of the user
        email (str): Primary email of the user
        company (str): Company the user is associated with
        location (str): Location of the user
        social_profile (str): Link to the user's social profile
        create_time (DateTime): Time when the user was created
    """
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, unique=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    social_profile = Column(String, nullable=True)
    create_time = Column(DateTime, nullable=False, default=current_timestamp())

    organizations = relationship("Organization",
                                 secondary=organization_user, back_populates="users")
    access_tokens = relationship("AccessToken", back_populates="user")

    def __init__(self, db: Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        while True:
            unique_id = random.randint(10000000000, 99999999999)
            if not db.query(User).filter(User.id == unique_id).first():
                self.id = unique_id
                if self.is_valid_email(self.email) and self.is_valid_username(self.username):
                    db.add(self)
                    db.commit()
                    break

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', " \
               f"company='{self.company}', location='{self.location}', " \
               f"social_profile='{self.social_profile}')>"

    @staticmethod
    def is_valid_email(email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def is_valid_username(username):
        username_regex = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,38}$'
        return re.match(username_regex, username) is not None
