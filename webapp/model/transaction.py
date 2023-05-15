"""
transaction.py contains the Transaction model.
"""
from sqlalchemy import Column, BigInteger, Float, String, DateTime
from sqlalchemy.sql.expression import func
from .database import Base


class Transaction(Base):
    """
    Transaction model

    Attributes:
        id (int): Unique auto-increment integer identifier for the transaction
        organization_id (int): Foreign key for the organization associated with the transaction
        user_id (int): Foreign key for the user associated with the transaction
        prompt_tokens (int): Number of tokens used for the prompt
        completion_tokens (int): Number of tokens used for the completion
        cost (float): Cost of the transaction
        currency (str): Currency of the cost
        create_time (datetime): Time when the transaction was created
    """
    __tablename__ = 'transactions'

    id = Column(BigInteger, primary_key=True, unique=True)
    organization_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    prompt_tokens = Column(BigInteger, nullable=False)
    completion_tokens = Column(BigInteger, nullable=False)
    cost = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    create_time = Column(DateTime(timezone=True), nullable=False,
                         default=func.now())  # pylint: disable=E1102

    def __repr__(self):
        return f"<Transaction(id={self.id}, " \
               f"organization_id={self.organization_id}, user_id={self.user_id}, " \
               f"prompt_tokens={self.prompt_tokens}, completion_tokens={self.completion_tokens}, " \
               f"cost={self.cost}, currency={self.currency}, create_time='{self.create_time}')>"
