from sqlalchemy import Column, ForeignKey
from sqlalchemy import BigInteger, Float, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func
from .database import Base


class Payment(Base):
    """
    Payment model

    Attributes:
        id (int): Unique integer identifier for the payment
        organization_id (int): Foreign key referencing the organization's ID
        amount (float): The amount of the payment
        currency (str): The currency of the payment (default to 'USD')
        create_time (datetime): The time when the payment was made
    """
    __tablename__ = 'payments'

    id = Column(BigInteger, primary_key=True, unique=True)
    organization_id = Column(BigInteger, ForeignKey('organizations.id'))
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default='USD')
    create_time = Column(DateTime(timezone=True), nullable=False,
                         default=func.now())  # pylint: disable=E1102

    organization = relationship("Organization", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, organization_id={self.organization_id}, " \
               f"amount={self.amount}, currency='{self.currency}', " \
               f"create_time='{self.create_time}')>"
