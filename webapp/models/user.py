# user.py
import random
import re
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from webapp.database import Base, Session
from webapp.models import organization_user


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
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    social_profile = Column(String, nullable=True)
    organizations = relationship("Organization",
                                 secondary=organization_user, back_populates="users")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with Session() as session:
            while True:
                unique_id = random.randint(1000000000, 9999999999)
                if not session.query(User).filter(User.id == unique_id).first():
                    self.id = unique_id
                    if self.is_valid_email(self.email) and self.is_valid_username(self.username):
                        session.add(self)
                        session.commit()
                        break

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', \
                company='{self.company}', location='{self.location}', \
                social_profile='{self.social_profile}')>"

    @staticmethod
    def is_valid_email(email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def is_valid_username(username):
        username_regex = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,38}$'
        return re.match(username_regex, username) is not None
