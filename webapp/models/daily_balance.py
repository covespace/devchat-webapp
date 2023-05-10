"""
daily_balance.py contains the DailyBalance model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from webapp.database import Base


class DailyBalance(Base):
    """
    DailyBalance model

    Attributes:
        id (int): Unique auto-increment integer identifier for the daily balance
        date (datetime): Date of the daily balance
        organization_id (int): Foreign key for the organization associated with the daily balance
        prompt_token_sum (int): Sum of prompt tokens for the day
        completion_token_sum (int): Sum of completion tokens for the day
        balance (float): Balance of the organization at the end of the day
    """
    __tablename__ = 'daily_balances'

    id = Column(Integer, primary_key=True, unique=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    prompt_token_sum = Column(Integer, nullable=False)
    completion_token_sum = Column(Integer, nullable=False)
    balance = Column(Float, nullable=False)

    organization = relationship("Organization", back_populates="daily_balances")

    def __repr__(self):
        return f"<DailyBalance(id={self.id}, date='{self.date}', \
                organization_id={self.organization_id}, \
                prompt_token_sum={self.prompt_token_sum}, \
                completion_token_sum={self.completion_token_sum}, \
                balance={self.balance})>"
