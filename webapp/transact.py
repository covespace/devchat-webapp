"""
transact.py contains functions for making transactions.
"""
from datetime import datetime
from typing import List
from sqlalchemy import and_, func
from webapp.database import Session
from webapp.models import Organization, Transaction, Balance, Payment


def add_transactions_batch(transactions: List[Transaction]) -> bool:
    """
    Add a batch of transactions to the transactions table.

    Args:
        transactions (list): A list of Transaction objects to be added to the database.

    Returns:
        bool: True if the transactions were added successfully, False otherwise.
    """
    session = Session()
    try:
        session.add_all(transactions)
        session.commit()
        return True
    except Exception as exc:
        print(f"Error adding transactions batch: {exc}")
        session.rollback()
        return False
    finally:
        session.close()


def calculate_balances(organization_ids=None):
    session = Session()

    if organization_ids is None:
        organization_ids = [org.id for org in session.query(Organization.id).all()]

    last_balances = session.query(
        Balance.organization_id,
        Balance.timestamp,
        Balance.balance
    ).filter(
        and_(
            Balance.id.in_(
                session.query(func.max(Balance.id)).  # pylint: disable=E1102
                group_by(Balance.organization_id)
            ),
            Balance.organization_id.in_(organization_ids)
        )
    ).all()

    balances = []

    # Get a single timestamp for all balances
    current_time = datetime.utcnow()

    # Store organization IDs in a dictionary
    org_id_dict = {org_id: (None, 0) for org_id in organization_ids}
    for org_id, last_time, last_balance in last_balances:
        org_id_dict[org_id] = (last_time, last_balance)

    for org_id, (last_time, last_balance) in org_id_dict.items():
        transactions = session.query(Transaction).filter(
            Transaction.organization_id == org_id,
            Transaction.timestamp > (last_time if last_time else datetime.min),
            Transaction.timestamp <= current_time
        ).all()

        payments = session.query(Payment).filter(
            Payment.organization_id == org_id,
            Payment.timestamp > (last_time if last_time else datetime.min),
            Payment.timestamp <= current_time
        ).all()

        prompt_token_sum = sum(transaction.prompt_tokens for transaction in transactions)
        completion_token_sum = sum(transaction.completion_tokens for transaction in transactions)
        cost_sum = sum(transaction.price for transaction in transactions)
        payment_sum = sum(payment.amount for payment in payments)

        new_balance = last_balance - cost_sum + payment_sum

        balance = Balance(organization_id=org_id, timestamp=current_time,
                          prompt_token_sum=prompt_token_sum,
                          completion_token_sum=completion_token_sum,
                          balance=new_balance)

        session.add(balance)
        balances.append((org_id, new_balance))

    session.commit()
    session.close()

    return balances
