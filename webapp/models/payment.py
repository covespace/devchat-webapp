from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Float, String, DateTime
from sqlalchemy.orm import relationship
from webapp.database import Base
from webapp.utils import current_timestamp


class Payment(Base):
    """
    Payment model

    Attributes:
        id (int): Unique integer identifier for the payment
        organization_id (int): Foreign key referencing the organization's ID
        amount (float): The amount of the payment
        currency (str): The currency of the payment (default to 'USD')
        timestamp (datetime): The timestamp when the payment was made
    """
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, unique=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    timestamp = Column(DateTime, nullable=False, default=current_timestamp())

    organization = relationship("Organization", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, organization_id={self.organization_id}, \
                 amount={self.amount}, currency='{self.currency}', timestamp='{self.timestamp}')>"
