"""
organization.py contains the Organization model.
"""
import random
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from webapp.database import Base, Session

organization_user = Table(
    'organization_user',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class Organization(Base):
    """
    Organization model

    Attributes:
        id (int): Unique integer identifier for the organization
        name (str): Name of the organization
        balance (float): Current balance of the organization
        currency (str): Currency of the balance
        country_code (str): Location of the organization
    """
    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, unique=True, nullable=False)
    balance = Column(Float, nullable=False, default=0)
    currency = Column(String, nullable=False, default='USD')
    country_code = Column(String, nullable=False)
    users = relationship("User", secondary=organization_user, back_populates="organizations")
    access_tokens = relationship("AccessToken", back_populates="organization")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with Session() as session:
            while True:
                unique_id = random.randint(10000000, 99999999)
                if not session.query(Organization).filter(Organization.id == unique_id).first():
                    self.id = unique_id
                    session.add(self)
                    session.commit()
                    break

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', \
                balance={self.balance}, currency='{self.currency}', \
                country_code='{self.country_code}')>"
