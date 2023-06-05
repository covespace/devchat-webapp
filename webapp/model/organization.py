"""
organization.py contains the Organization model.
"""
from enum import Enum
import random
from sqlalchemy import Column, ForeignKey, Table, Enum as SqlEnum
from sqlalchemy import String, Float, BigInteger, DateTime
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql.expression import func
from webapp.utils import is_valid_account_name
from .database import Base
from .balance import Balance  # pylint: disable=unused-import
from .payment import Payment  # pylint: disable=unused-import


class Role(str, Enum):
    OWNER = "owner"
    MEMBER = "member"


organization_user = Table(
    'organization_user',
    Base.metadata,
    Column('organization_id', BigInteger, ForeignKey('organizations.id')),
    Column('user_id', BigInteger, ForeignKey('users.id')),
    Column('role', SqlEnum(Role), nullable=False, default=Role.MEMBER)
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
        create_time (DateTime): Time when the organization was created
    """
    __tablename__ = 'organizations'

    id = Column(BigInteger, primary_key=True, unique=True)
    name = Column(String, unique=True, nullable=False)
    balance = Column(Float, nullable=False, default=0)
    currency = Column(String, nullable=False, default='USD')
    country_code = Column(String, nullable=True)
    create_time = Column(DateTime(timezone=True), nullable=False,
                         default=func.now())  # pylint: disable=E1102

    users = relationship("User", secondary=organization_user, back_populates="organizations")
    access_keys = relationship("AccessKey", back_populates="organization")
    balances = relationship("Balance", back_populates="organization")
    payments = relationship("Payment", back_populates="organization")

    def __init__(self, db: Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not is_valid_account_name(self.name):
            raise ValueError("Invalid organization name provided.")

        with db.begin_nested():
            while True:
                unique_id = random.randint(10000000000, 99999999999)
                if not db.query(Organization).filter(Organization.id == unique_id).first():
                    self.id = unique_id
                    break
            db.add(self)
            db.commit()

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', " \
               f"balance={self.balance}, currency='{self.currency}', " \
               f"country_code='{self.country_code}')>"
