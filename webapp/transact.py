"""
transact.py contains functions for making transactions.
"""
from typing import List
from webapp.database import Session
from webapp.models import Transaction


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
