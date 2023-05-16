"""
balance.py contains the Balance model.
"""
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Float, String
from sqlalchemy.orm import relationship
from .database import Base


class Balance(Base):
    """
    Balance model

    Attributes:
        id (int): Unique auto-increment Biginteger identifier for the balance
        timestamp (DateTime): Timestamp of the balance
        organization_id (int): Foreign key for the organization associated with the balance
        prompt_token_sum (int): Sum of prompt tokens since the last timestamp
        response_token_sum (int): Sum of response tokens since the last timestamp
        balance (float): Balance of the organization at the timestamp
        currency (str): Currency of the balance
    """
    __tablename__ = 'balances'

    id = Column(BigInteger, primary_key=True, unique=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    organization_id = Column(BigInteger, ForeignKey('organizations.id'))
    prompt_token_sum = Column(BigInteger, nullable=False)
    response_token_sum = Column(BigInteger, nullable=False)
    balance = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')

    organization = relationship("Organization", back_populates="balances")

    def __repr__(self):
        return f"<Balance(id={self.id}, timestamp='{self.timestamp}', " \
               f"organization_id={self.organization_id}, " \
               f"prompt_token_sum={self.prompt_token_sum}, " \
               f"response_token_sum={self.response_token_sum}, " \
               f"balance={self.balance}, currency={self.currency})>"
