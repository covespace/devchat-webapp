# test_management.py
import pytest
from webapp.database import Base, engine, Session, create_tables
from webapp.models import Organization
from webapp.management import create_organization
from webapp.models import User
from webapp.management import create_user, add_user_to_organization


@pytest.fixture(scope="function", name="setup_database")
def fixture_setup_database():
    create_tables()
    yield
    # Clean up the database after each test
    Base.metadata.drop_all(engine)


def test_create_organization_success(setup_database):  # pylint: disable=unused-argument
    name = "Test Organization"
    country_code = "USA"
    organization = create_organization(name, country_code)

    assert organization.name == name
    assert organization.country_code == country_code
    assert organization.balance == 0
    assert organization.currency == "USD"

    session = Session()
    db_organization = session.query(Organization).filter_by(id=organization.id).first()
    session.close()

    assert db_organization is not None
    assert db_organization.name == name
    assert db_organization.country_code == country_code
    assert db_organization.balance == 0
    assert db_organization.currency == "USD"


def test_create_organization_duplicate_name(setup_database):  # pylint: disable=unused-argument
    name = "Duplicate Organization"
    country_code = "US"
    create_organization(name, country_code)

    with pytest.raises(Exception):
        create_organization(name, country_code)


def test_create_user_success(setup_database):  # pylint: disable=unused-argument
    username = "testuser"
    email = "testuser@example.com"
    company = "Test Company"
    location = "Test City"
    social_profile = "https://example.com/testuser"

    user = create_user(username, email, company, location, social_profile)

    assert user.username == username
    assert user.email == email
    assert user.company == company
    assert user.location == location
    assert user.social_profile == social_profile

    session = Session()
    db_user = session.query(User).filter_by(id=user.id).first()
    session.close()

    assert db_user is not None
    assert db_user.username == username
    assert db_user.email == email
    assert db_user.company == company
    assert db_user.location == location
    assert db_user.social_profile == social_profile


def test_create_user_duplicate_username(setup_database):  # pylint: disable=unused-argument
    username = "duplicateuser"
    email = "duplicateuser@example.com"

    create_user(username, email)

    with pytest.raises(Exception):
        create_user(username, "anotheremail@example.com")


def test_add_user_to_organization_success(setup_database):  # pylint: disable=unused-argument
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(username, email)

    result = add_user_to_organization(user.id, organization.id)

    assert result is True

    session = Session()
    db_organization = session.query(Organization).filter_by(id=organization.id).first()
    assert db_organization is not None
    users = db_organization.users
    session.close()

    assert len(users) == 1
    assert users[0].id == user.id


def test_add_user_to_organization_invalid_ids(setup_database):  # pylint: disable=unused-argument
    result = add_user_to_organization(999, 999)
    assert result is False
