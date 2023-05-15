"""
test_transact.py contains tests for the transact.py module.
"""
from datetime import timedelta
import time
import pytest
from webapp.model import Transaction, Payment
from webapp.controller import create_organization, create_user
from webapp.controller import add_transactions_batch, calculate_balances
from webapp.utils import now


def _simulate_now(database):
    """
    Get current time minus two seconds.
    To avoid clock drift, balances are calculated against a slightly earlier timepoint.
    """
    return now(database) - timedelta(seconds=2)


def _call_calculate_balances(database):
    """
    Call calculate_balances() after delaying 1 second.
    """
    try:
        return calculate_balances(database)
    finally:
        time.sleep(1)


def test_add_transactions_batch_success(database):
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    transactions = [
        Transaction(organization_id=organization.id, user_id=user.id,
                    prompt_tokens=10, completion_tokens=20, cost=0.1,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=organization.id, user_id=user.id,
                    prompt_tokens=15, completion_tokens=25, cost=0.15,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=organization.id, user_id=user.id,
                    prompt_tokens=20, completion_tokens=30, cost=0.2,
                    create_time=_simulate_now(database))
    ]

    result = add_transactions_batch(database, transactions)
    assert result is True

    db_transactions = database.query(Transaction).filter_by(organization_id=organization.id).all()

    assert len(db_transactions) == 3
    assert db_transactions[0].prompt_tokens == 10
    assert db_transactions[1].completion_tokens == 25
    assert db_transactions[2].cost == 0.2


def test_add_transactions_batch_invalid_transactions(database):
    invalid_transactions = [
        {"organization_id": 1, "user_id": 1,
         "prompt_tokens": 10, "completion_tokens": 20, "cost": 0.1},
        {"organization_id": 1, "user_id": 1,
         "prompt_tokens": 15, "completion_tokens": 25, "cost": 0.15},
        {"organization_id": 1, "user_id": 1,
         "prompt_tokens": 20, "completion_tokens": 30, "cost": 0.2}
    ]

    with pytest.raises(Exception):
        add_transactions_batch(database, invalid_transactions)

    db_transactions = database.query(Transaction).all()

    assert len(db_transactions) == 0


def test_balances_multiple_organizations(database):  # pylint: disable=W0613
    # Create two organizations
    org1 = create_organization(database, "Org1", "USA")
    org2 = create_organization(database, "Org2", "USA")

    # Create a user
    user = create_user(database, "testuser", "testuser@example.com")

    # Add transactions for each organization
    transactions_org1 = [
        Transaction(organization_id=org1.id, user_id=user.id,
                    prompt_tokens=10, completion_tokens=20, cost=0.1,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org1.id, user_id=user.id,
                    prompt_tokens=15, completion_tokens=25, cost=0.15,
                    create_time=_simulate_now(database))
    ]
    transactions_org2 = [
        Transaction(organization_id=org2.id, user_id=user.id,
                    prompt_tokens=20, completion_tokens=30, cost=0.2,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org2.id, user_id=user.id,
                    prompt_tokens=25, completion_tokens=35, cost=0.25,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions_org1)
    add_transactions_batch(database, transactions_org2)

    # Calculate balances
    balances = _call_calculate_balances(database)

    # Check if the balances are calculated correctly
    assert len(balances) == 2

    org1_balance = next(balance for org_id, balance in balances if org_id == org1.id)
    org2_balance = next(balance for org_id, balance in balances if org_id == org2.id)

    assert org1_balance == -0.25
    assert org2_balance == -0.45


def test_balances_no_transactions(database):
    # Create an organization
    org = create_organization(database, "Org1", "USA")

    # Calculate balances
    balances = _call_calculate_balances(database)

    # Check if the balance is 0 for the organization with no transactions
    assert len(balances) == 1
    org_balance = next(balance for org_id, balance in balances if org_id == org.id)
    assert org_balance == 0


def test_balances_multiple_users(database):
    # Create an organization
    org = create_organization(database, "Org1", "USA")

    # Create two users
    user1 = create_user(database, "testuser1", "testuser1@example.com")
    user2 = create_user(database, "testuser2", "testuser2@example.com")

    # Add transactions for each user
    transactions_user1 = [
        Transaction(organization_id=org.id, user_id=user1.id,
                    prompt_tokens=10, completion_tokens=20, cost=0.1,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org.id, user_id=user1.id,
                    prompt_tokens=15, completion_tokens=25, cost=0.15,
                    create_time=_simulate_now(database))
    ]
    transactions_user2 = [
        Transaction(organization_id=org.id, user_id=user2.id,
                    prompt_tokens=20, completion_tokens=30, cost=0.2,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org.id, user_id=user2.id,
                    prompt_tokens=25, completion_tokens=35, cost=0.25,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions_user1)
    add_transactions_batch(database, transactions_user2)

    # Calculate balances
    balances = _call_calculate_balances(database)

    # Check if the balance is calculated correctly for the organization with multiple users
    assert len(balances) == 1
    org_balance = next(balance for org_id, balance in balances if org_id == org.id)
    assert org_balance == -0.7


def test_balances_single_organization_interleaved_transactions(database):
    # Create an organization
    org = create_organization(database, "Org1", "USA")

    # Create a user
    user = create_user(database, "testuser", "testuser@example.com")

    # Add transactions for the user
    transactions1 = [
        Transaction(organization_id=org.id, user_id=user.id,
                    prompt_tokens=10, completion_tokens=20, cost=0.1,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org.id, user_id=user.id,
                    prompt_tokens=15, completion_tokens=25, cost=0.15,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions1)

    # Calculate balances after the first batch of transactions
    balances1 = _call_calculate_balances(database)

    # Add more transactions for the user
    transactions2 = [
        Transaction(organization_id=org.id, user_id=user.id,
                    prompt_tokens=20, completion_tokens=30, cost=0.2,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org.id, user_id=user.id,
                    prompt_tokens=25, completion_tokens=35, cost=0.25,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions2)

    # Calculate balances after the second batch of transactions
    balances2 = _call_calculate_balances(database)

    # Check if the balances are calculated correctly after each batch of transactions
    assert len(balances1) == 1
    org_balance1 = next(balance for org_id, balance in balances1 if org_id == org.id)
    assert org_balance1 == -0.25

    assert len(balances2) == 1
    org_balance2 = next(balance for org_id, balance in balances2 if org_id == org.id)
    assert org_balance2 == -0.7


def test_balances_multiple_organizations_interleaved_transactions(database):
    # Create two organizations
    org1 = create_organization(database, "Org1", "USA")
    org2 = create_organization(database, "Org2", "USA")

    # Create a user
    user = create_user(database, "testuser", "testuser@example.com")

    # Add transactions for the user in the first organization
    transactions_org1 = [
        Transaction(organization_id=org1.id, user_id=user.id,
                    prompt_tokens=10, completion_tokens=20, cost=0.1,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org1.id, user_id=user.id,
                    prompt_tokens=15, completion_tokens=25, cost=0.15,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions_org1)

    # Calculate balances after the first batch of transactions
    balances1 = _call_calculate_balances(database)

    # Add transactions for the user in the second organization
    transactions_org2 = [
        Transaction(organization_id=org2.id, user_id=user.id,
                    prompt_tokens=20, completion_tokens=30, cost=0.2,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org2.id, user_id=user.id,
                    prompt_tokens=25, completion_tokens=35, cost=0.25,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions_org2)

    # Calculate balances after the second batch of transactions
    balances2 = _call_calculate_balances(database)

    # Check if the balances are calculated correctly after each batch of transactions
    assert len(balances1) == 2
    org1_balance1 = next(balance for org_id, balance in balances1 if org_id == org1.id)
    org2_balance1 = next(balance for org_id, balance in balances1 if org_id == org2.id)
    assert org1_balance1 == -0.25
    assert org2_balance1 == 0

    assert len(balances2) == 2
    org1_balance2 = next(balance for org_id, balance in balances2 if org_id == org1.id)
    org2_balance2 = next(balance for org_id, balance in balances2 if org_id == org2.id)
    assert org1_balance2 == -0.25
    assert org2_balance2 == -0.45


def test_balances_with_payments(database):
    # Create an organization
    org = create_organization(database, "Org1", "USA")

    # Create a user
    user = create_user(database, "testuser", "testuser@example.com")

    # Add transactions for the user
    transactions = [
        Transaction(organization_id=org.id, user_id=user.id,
                    prompt_tokens=10, completion_tokens=20, cost=0.1,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org.id, user_id=user.id,
                    prompt_tokens=15, completion_tokens=25, cost=0.15,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions)

    # Add payments for the organization
    payments = [
        Payment(organization_id=org.id, amount=0.2, create_time=_simulate_now(database)),
        Payment(organization_id=org.id, amount=0.1, create_time=_simulate_now(database))
    ]
    database.add_all(payments)
    database.commit()

    # Calculate balances
    balances = _call_calculate_balances(database)

    # Check if the balance is calculated correctly with payments
    assert len(balances) == 1
    org_balance = next(balance for org_id, balance in balances if org_id == org.id)
    assert org_balance == pytest.approx(-0.25 + 0.2 + 0.1, rel=1e-9)


def test_balances_interleaved_transactions_payments(database):
    # Create an organization
    org = create_organization(database, "Org1", "USA")

    # Create a user
    user = create_user(database, "testuser", "testuser@example.com")

    # Add a transaction for the user
    transaction1 = Transaction(organization_id=org.id, user_id=user.id,
                               prompt_tokens=10, completion_tokens=20, cost=0.1,
                               create_time=_simulate_now(database))
    add_transactions_batch(database, [transaction1])

    # Calculate balances after the first transaction
    balances1 = _call_calculate_balances(database)

    # Add a payment for the organization
    payment1 = Payment(organization_id=org.id, amount=0.2, create_time=_simulate_now(database))
    database.add(payment1)
    database.commit()

    # Calculate balances after the first payment
    balances2 = _call_calculate_balances(database)

    # Add another transaction for the user
    transaction2 = Transaction(organization_id=org.id, user_id=user.id,
                               prompt_tokens=15, completion_tokens=25, cost=0.15,
                               create_time=_simulate_now(database))
    add_transactions_batch(database, [transaction2])

    # Calculate balances after the second transaction
    balances3 = _call_calculate_balances(database)

    # Add another payment for the organization
    payment2 = Payment(organization_id=org.id, amount=0.1, create_time=_simulate_now(database))
    database.add(payment2)
    database.commit()

    # Calculate balances after the second payment
    balances4 = _call_calculate_balances(database)

    # Check if the balances are calculated correctly at each step
    assert len(balances1) == 1
    org_balance1 = next(balance for org_id, balance in balances1 if org_id == org.id)
    assert org_balance1 == pytest.approx(-0.1, rel=1e-9)

    assert len(balances2) == 1
    org_balance2 = next(balance for org_id, balance in balances2 if org_id == org.id)
    assert org_balance2 == pytest.approx(-0.1 + 0.2, rel=1e-9)

    assert len(balances3) == 1
    org_balance3 = next(balance for org_id, balance in balances3 if org_id == org.id)
    assert org_balance3 == pytest.approx(-0.1 + 0.2 - 0.15, rel=1e-9)

    assert len(balances4) == 1
    org_balance4 = next(balance for org_id, balance in balances4 if org_id == org.id)
    assert org_balance4 == pytest.approx(-0.1 + 0.2 - 0.15 + 0.1, rel=1e-9)


def test_balances_with_transactions_and_payments(database):
    # Create organizations
    org1 = create_organization(database, "Org1", "USA")
    org2 = create_organization(database, "Org2", "UK")

    # Create users
    user1 = create_user(database, "testuser1", "testuser1@example.com")
    user2 = create_user(database, "testuser2", "testuser2@example.com")

    # Add transactions for the users
    transactions1 = [
        Transaction(organization_id=org1.id, user_id=user1.id,
                    prompt_tokens=10, completion_tokens=20, cost=0.1,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org2.id, user_id=user2.id,
                    prompt_tokens=15, completion_tokens=25, cost=0.15,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions1)

    # Calculate balances after the first transactions
    balances1 = _call_calculate_balances(database)

    # Add payments for the organizations
    payments1 = [
        Payment(organization_id=org1.id, amount=0.2, create_time=_simulate_now(database)),
        Payment(organization_id=org2.id, amount=0.25, create_time=_simulate_now(database))
    ]
    database.add_all(payments1)
    database.commit()

    # Add more transactions for the users
    transactions2 = [
        Transaction(organization_id=org1.id, user_id=user1.id,
                    prompt_tokens=20, completion_tokens=30, cost=0.2,
                    create_time=_simulate_now(database)),
        Transaction(organization_id=org2.id, user_id=user2.id,
                    prompt_tokens=25, completion_tokens=35, cost=0.25,
                    create_time=_simulate_now(database))
    ]
    add_transactions_batch(database, transactions2)

    # Add more payments for the organizations
    payments2 = [
        Payment(organization_id=org1.id, amount=0.3, create_time=_simulate_now(database)),
        Payment(organization_id=org2.id, amount=0.35, create_time=_simulate_now(database))
    ]
    database.add_all(payments2)
    database.commit()

    # Calculate balances after transactions and payments
    balances2 = _call_calculate_balances(database)

    # Check if the balances are calculated correctly for each organization at each step
    org1_balance1 = next(balance for org_id, balance in balances1 if org_id == org1.id)
    org2_balance1 = next(balance for org_id, balance in balances1 if org_id == org2.id)
    assert org1_balance1 == pytest.approx(-0.1, rel=1e-9)
    assert org2_balance1 == pytest.approx(-0.15, rel=1e-9)

    org1_balance2 = next(balance for org_id, balance in balances2 if org_id == org1.id)
    org2_balance2 = next(balance for org_id, balance in balances2 if org_id == org2.id)
    assert org1_balance2 == pytest.approx(-0.1 + 0.2 - 0.2 + 0.3, rel=1e-9)
    assert org2_balance2 == pytest.approx(-0.15 + 0.25 - 0.25 + 0.35, rel=1e-9)
