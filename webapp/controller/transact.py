"""
transact.py contains functions for making transactions.
"""
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from webapp.model import Organization, Transaction, Balance, Payment
from webapp.utils import now, get_logger

logger = get_logger(__name__)


def add_transactions_batch(db: Session, transactions: List[Transaction]):
    """
    Add a batch of transactions to the transactions table.

    Args:
        transactions (list): A list of Transaction objects to be added to the database.
    """
    try:
        db.add_all(transactions)
        db.commit()
        logger.info("Added %d transactions to the database", len(transactions))
        return True
    except Exception as exc:
        db.rollback()
        raise exc


def calculate_balances(db: Session, organization_ids=None):
    if organization_ids is None:
        organization_ids = [org.id for org in db.query(Organization.id).all()]

    last_balances = db.query(
        Balance.organization_id,
        Balance.timestamp,
        Balance.balance
    ).filter(
        and_(
            Balance.id.in_(
                db.query(func.max(Balance.id)).  # pylint: disable=E1102
                group_by(Balance.organization_id)
            ),
            Balance.organization_id.in_(organization_ids)
        )
    ).all()

    balances = []

    # Get a single timestamp for all balances
    timestamp = now(db).replace(microsecond=0) - timedelta(seconds=1)

    # Store organization IDs in a dictionary
    org_id_dict = {org_id: (None, 0) for org_id in organization_ids}
    for org_id, last_time, last_balance in last_balances:
        org_id_dict[org_id] = (last_time, last_balance)

    for org_id, (last_time, last_balance) in org_id_dict.items():
        transactions = db.query(Transaction).filter(
            Transaction.organization_id == org_id,
            Transaction.create_time > (last_time if last_time else datetime.min),
            Transaction.create_time <= timestamp
        ).all()

        payments = db.query(Payment).filter(
            Payment.organization_id == org_id,
            Payment.create_time > (last_time if last_time else datetime.min),
            Payment.create_time <= timestamp
        ).all()

        prompt_token_sum = sum(transaction.prompt_tokens for transaction in transactions)
        response_token_sum = sum(transaction.response_tokens for transaction in transactions)
        cost_sum = sum(transaction.cost for transaction in transactions)
        payment_sum = sum(payment.amount for payment in payments)

        new_balance = last_balance - cost_sum + payment_sum

        balance = Balance(organization_id=org_id, timestamp=timestamp,
                          prompt_token_sum=prompt_token_sum,
                          response_token_sum=response_token_sum,
                          balance=new_balance)

        db.add(balance)
        balances.append((org_id, new_balance))

    db.commit()
    logger.info("Calculated balances for %d organizations", len(balances))
    return balances
