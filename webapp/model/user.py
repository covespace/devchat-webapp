"""
user.py contains the User model.
"""
import random
from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql.expression import func
from webapp.utils import is_valid_email, is_valid_account_name
from .database import Base
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
    email = Column(String, unique=True, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    social_profile = Column(String, nullable=True)
    create_time = Column(DateTime(timezone=True), nullable=False,
                         default=func.now())  # pylint: disable=E1102

    organizations = relationship("Organization",
                                 secondary=organization_user, back_populates="users")
    access_keys = relationship("AccessKey", back_populates="user")

    def __init__(self, db: Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_valid_email(self.email):
            raise ValueError("Invalid email provided.")
        if not is_valid_account_name(self.username):
            raise ValueError("Invalid username provided.")

        with db.begin_nested():
            while True:
                unique_id = random.randint(10000000000, 99999999999)
                if not db.query(User).filter(User.id == unique_id).first():
                    self.id = unique_id
                    break
            db.add(self)
            db.commit()

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', " \
               f"company='{self.company}', location='{self.location}', " \
               f"social_profile='{self.social_profile}')>"
