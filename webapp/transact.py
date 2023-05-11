"""
transact.py contains functions for making transactions.
"""
from datetime import datetime
from typing import List
from sqlalchemy import and_, func
from webapp.database import Session
from webapp.models import Organization, Transaction, DailyBalance


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


def calculate_daily_balances(organization_ids=None):
    session = Session()

    if organization_ids is None:
        organization_ids = [org.id for org in session.query(Organization.id).all()]

    last_daily_balances = session.query(
        DailyBalance.organization_id,
        DailyBalance.timestamp,
        DailyBalance.balance
    ).filter(
        and_(
            DailyBalance.id.in_(
                session.query(func.max(DailyBalance.id)).  # pylint: disable=E1102
                group_by(DailyBalance.organization_id)
            ),
            DailyBalance.organization_id.in_(organization_ids)
        )
    ).all()

    daily_balances = []

    # Get a single timestamp for all daily balances
    current_time = datetime.utcnow()

    # Store organization IDs in a dictionary
    org_id_dict = {org_id: (None, 0) for org_id in organization_ids}
    for org_id, last_time, last_balance in last_daily_balances:
        org_id_dict[org_id] = (last_time, last_balance)

    for org_id, (last_time, last_balance) in org_id_dict.items():
        transactions = session.query(Transaction).filter(
            Transaction.organization_id == org_id,
            Transaction.timestamp > (last_time if last_time else datetime.min),
            Transaction.timestamp <= current_time
        ).all()

        prompt_token_sum = sum(transaction.prompt_tokens for transaction in transactions)
        completion_token_sum = sum(transaction.completion_tokens for transaction in transactions)
        cost_sum = sum(transaction.price for transaction in transactions)

        new_balance = last_balance - cost_sum

        daily_balance = DailyBalance(organization_id=org_id, timestamp=current_time,
                                     prompt_token_sum=prompt_token_sum,
                                     completion_token_sum=completion_token_sum,
                                     balance=new_balance)

        session.add(daily_balance)
        daily_balances.append((org_id, new_balance))

    session.commit()
    session.close()

    return daily_balances
