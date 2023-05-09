"""
test_query.py contains tests for the query.py module.
"""
import pytest
from webapp.database import Base, engine, create_tables
from webapp.management import create_organization, create_user, add_user_to_organization
from webapp.query import get_users_of_organization


@pytest.fixture(scope="function", name="setup_database")
def fixture_setup_database():
    create_tables()
    yield
    # Clean up the database after each test
    Base.metadata.drop_all(engine)


def test_get_users_of_organization_success(setup_database):  # pylint: disable=unused-argument
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(org_name, country_code)

    username1 = "testuser1"
    email1 = "testuser1@example.com"
    user1 = create_user(username1, email1)

    username2 = "testuser2"
    email2 = "testuser2@example.com"
    user2 = create_user(username2, email2)

    add_user_to_organization(user1.id, organization.id)
    add_user_to_organization(user2.id, organization.id)

    users = get_users_of_organization(organization.id)

    assert len(users) == 2
    assert [user1.id, username1, email1] in users
    assert [user2.id, username2, email2] in users


def test_get_users_of_organization_custom_columns(setup_database):  # pylint: disable=W0613
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    company = "Test Company"
    location = "Test City"
    social_profile = "https://example.com/testuser"
    user = create_user(username, email, company, location, social_profile)

    add_user_to_organization(user.id, organization.id)

    users = get_users_of_organization(organization.id, columns=['id', 'location', 'company'])

    assert len(users) == 1
    assert [user.id, location, company] in users


def test_get_users_of_organization_invalid_id(setup_database):  # pylint: disable=unused-argument
    users = get_users_of_organization(999)
    assert users == []
