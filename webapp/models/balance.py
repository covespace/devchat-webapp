"""
balance.py contains the Balance model.
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from webapp.database import Base


class Balance(Base):
    """
    Balance model

    Attributes:
        id (int): Unique auto-increment integer identifier for the balance
        timestamp (DateTime): Timestamp of the balance
        organization_id (int): Foreign key for the organization associated with the balance
        prompt_token_sum (int): Sum of prompt tokens since the last timestamp
        completion_token_sum (int): Sum of completion tokens since the last timestamp
        balance (float): Balance of the organization at the timestamp
    """
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True, unique=True)
    timestamp = Column(DateTime, nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    prompt_token_sum = Column(Integer, nullable=False)
    completion_token_sum = Column(Integer, nullable=False)
    balance = Column(Float, nullable=False)

    organization = relationship("Organization", back_populates="balances")

    def __repr__(self):
        return f"<Balance(id={self.id}, timestamp='{self.timestamp}', \
                organization_id={self.organization_id}, \
                prompt_token_sum={self.prompt_token_sum}, \
                completion_token_sum={self.completion_token_sum}, \
                balance={self.balance})>"
