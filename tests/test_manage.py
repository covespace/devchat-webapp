"""
test_management.py contains tests for the functions in management.py.
"""
import pytest
from webapp.model import Organization
from webapp.controller import create_organization
from webapp.model import User
from webapp.controller import create_user, add_user_to_organization
from webapp.model import AccessKey
from webapp.controller import create_access_token, revoke_access_token


def test_create_organization_success(database):
    name = "Test Organization"
    country_code = "USA"
    organization = create_organization(database, name, country_code)

    assert organization.name == name
    assert organization.country_code == country_code
    assert organization.balance == 0
    assert organization.currency == "USD"

    db_organization = database.query(Organization).filter_by(id=organization.id).first()

    assert db_organization is not None
    assert db_organization.name == name
    assert db_organization.country_code == country_code
    assert db_organization.balance == 0
    assert db_organization.currency == "USD"


def test_create_organization_duplicate_name(database):
    name = "Duplicate Organization"
    country_code = "US"
    create_organization(database, name, country_code)

    with pytest.raises(Exception):
        create_organization(database, name, country_code)


def test_create_user_success(database):
    username = "testuser"
    email = "testuser@example.com"
    company = "Test Company"
    location = "Test City"
    social_profile = "https://example.com/testuser"

    user = create_user(database, username, email, company, location, social_profile)

    assert user.username == username
    assert user.email == email
    assert user.company == company
    assert user.location == location
    assert user.social_profile == social_profile

    db_user = database.query(User).filter_by(id=user.id).first()

    assert db_user is not None
    assert db_user.username == username
    assert db_user.email == email
    assert db_user.company == company
    assert db_user.location == location
    assert db_user.social_profile == social_profile


def test_create_user_duplicate_username(database):
    username = "duplicateuser"
    email = "duplicateuser@example.com"

    create_user(database, username, email)

    with pytest.raises(Exception):
        create_user(database, username, "anotheremail@example.com")


def test_add_user_to_organization_success(database):
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    result = add_user_to_organization(database, user.id, organization.id)

    assert result is True

    db_organization = database.query(Organization).filter_by(id=organization.id).first()
    assert db_organization is not None
    users = db_organization.users

    assert len(users) == 1
    assert users[0].id == user.id


def test_add_user_to_organization_invalid_ids(database):
    result = add_user_to_organization(database, 999, 999)
    assert result is False


def test_create_token_success(database):
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    token_name = "Test Token"
    region = "US"
    token = create_access_token(database, user.id, organization.id, token_name, region)

    assert token.user_id == user.id
    assert token.organization_id == organization.id
    assert token.name == token_name
    assert token.revoke_time is None

    db_token = database.query(AccessKey).filter_by(id=token.id).first()

    assert db_token is not None
    assert db_token.user_id == user.id
    assert db_token.organization_id == organization.id
    assert db_token.name == token_name
    assert db_token.revoke_time is None


def test_create_token_invalid_region(database):
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    token_name = "Test Token"
    invalid_region = "USA123"

    with pytest.raises(ValueError):
        create_access_token(database, user.id, organization.id, token_name, invalid_region)


def test_revoke_token_success(database):
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(database, org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(database, username, email)

    token_name = "Test Token"
    region = "US"
    token = create_access_token(database, user.id, organization.id, token_name, region)

    result = revoke_access_token(database, token.id)

    assert result is True

    db_token = database.query(AccessKey).filter_by(id=token.id).first()

    assert db_token is not None
    assert db_token.revoke_time is not None


def test_revoke_token_invalid_id(database):
    result = revoke_access_token(database, 999)
    assert result is False
