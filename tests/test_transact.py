"""
test_transact.py contains tests for the transact.py module.
"""
import pytest
from webapp.database import Base, Session, engine, create_tables
from webapp.models import Transaction
from webapp.manage import create_organization, create_user
from webapp.transact import add_transactions_batch


@pytest.fixture(scope="function", name="setup_database")
def fixture_setup_database():
    create_tables()
    yield
    # Clean up the database after each test
    Base.metadata.drop_all(engine)


def test_add_transactions_batch_success(setup_database):  # pylint: disable=unused-argument
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(username, email)

    transactions = [
        Transaction(organization_id=organization.id, user_id=user.id,
                    prompt_tokens=10, completion_tokens=20, price=0.1),
        Transaction(organization_id=organization.id, user_id=user.id,
                    prompt_tokens=15, completion_tokens=25, price=0.15),
        Transaction(organization_id=organization.id, user_id=user.id,
                    prompt_tokens=20, completion_tokens=30, price=0.2)
    ]

    result = add_transactions_batch(transactions)
    assert result is True

    session = Session()
    db_transactions = session.query(Transaction).filter_by(organization_id=organization.id).all()
    session.close()

    assert len(db_transactions) == 3
    assert db_transactions[0].prompt_tokens == 10
    assert db_transactions[1].completion_tokens == 25
    assert db_transactions[2].price == 0.2


def test_add_transactions_batch_invalid_transactions(setup_database):  # pylint: disable=W0613
    invalid_transactions = [
        {"organization_id": 1, "user_id": 1,
         "prompt_tokens": 10, "completion_tokens": 20, "price": 0.1},
        {"organization_id": 1, "user_id": 1,
         "prompt_tokens": 15, "completion_tokens": 25, "price": 0.15},
        {"organization_id": 1, "user_id": 1,
         "prompt_tokens": 20, "completion_tokens": 30, "price": 0.2}
    ]

    result = add_transactions_batch(invalid_transactions)
    assert result is False

    session = Session()
    db_transactions = session.query(Transaction).all()
    session.close()

    assert len(db_transactions) == 0
