"""
transaction.py contains the Transaction model.
"""
from sqlalchemy import Column, Integer, Float, DateTime
from webapp.database import Base
from webapp.utils import current_timestamp


class Transaction(Base):
    """
    Transaction model

    Attributes:
        id (int): Unique auto-increment integer identifier for the transaction
        organization_id (int): Foreign key for the organization associated with the transaction
        user_id (int): Foreign key for the user associated with the transaction
        prompt_tokens (int): Number of tokens used for the prompt
        completion_tokens (int): Number of tokens used for the completion
        price (float): Price of the transaction
        timestamp (datetime): Time when the transaction was created
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, unique=True)
    organization_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=current_timestamp())

    def __repr__(self):
        return f"<Transaction(id={self.id}, \
                organization_id={self.organization_id}, user_id={self.user_id}, \
                prompt_tokens={self.prompt_tokens}, completion_tokens={self.completion_tokens}, \
                price={self.price}, timestamp='{self.timestamp}')>"
