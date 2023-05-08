from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Organization(Base):
    """
    Organization model

    Attributes:
        uuid (str): Unique string identifier for the organization
        name (str): Name of the organization
        balance (float): Current balance of the organization
        currency (str): Currency of the balance
        country_code (str): Location of the organization
    """
    __tablename__ = 'organizations'

    uuid = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    balance = Column(Float, nullable=False, default=0)
    currency = Column(String, nullable=False, default='USD')
    country_code = Column(String, nullable=False)

    def __repr__(self):
        return f"<Organization(uuid='{self.uuid}', name='{self.name}', \
                balance={self.balance}, currency='{self.currency}', \
                country_code='{self.country_code}')>"
