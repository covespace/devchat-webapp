"""
test_management.py contains tests for the functions in management.py.
"""
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import pytest
from webapp.database import Base, engine, Session, create_tables
from webapp.models import Organization
from webapp.management import create_organization
from webapp.models import User
from webapp.management import create_user, add_user_to_organization
from webapp.models import AccessToken
from webapp.management import create_access_token, revoke_access_token


@pytest.fixture(scope="module", autouse=True)
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    os.environ['JWT_PRIVATE_KEY'] = private_pem.decode('utf-8')
    os.environ['JWT_PUBLIC_KEY'] = public_pem.decode('utf-8')


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


def test_create_token_success(setup_database):  # pylint: disable=unused-argument
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(username, email)

    token_name = "Test Token"
    region = "US"
    token = create_access_token(user.id, organization.id, token_name, region)

    assert token.user_id == user.id
    assert token.organization_id == organization.id
    assert token.name == token_name
    assert token.revoke_time is None

    session = Session()
    db_token = session.query(AccessToken).filter_by(id=token.id).first()
    session.close()

    assert db_token is not None
    assert db_token.user_id == user.id
    assert db_token.organization_id == organization.id
    assert db_token.name == token_name
    assert db_token.revoke_time is None


def test_create_token_invalid_region(setup_database):  # pylint: disable=unused-argument
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(username, email)

    token_name = "Test Token"
    invalid_region = "USA123"

    with pytest.raises(ValueError):
        create_access_token(user.id, organization.id, token_name, invalid_region)


def test_revoke_token_success(setup_database):  # pylint: disable=unused-argument
    org_name = "Test Organization"
    country_code = "USA"
    organization = create_organization(org_name, country_code)

    username = "testuser"
    email = "testuser@example.com"
    user = create_user(username, email)

    token_name = "Test Token"
    region = "US"
    token = create_access_token(user.id, organization.id, token_name, region)

    result = revoke_access_token(token.id)

    assert result is True

    session = Session()
    db_token = session.query(AccessToken).filter_by(id=token.id).first()
    session.close()

    assert db_token is not None
    assert db_token.revoke_time is not None


def test_revoke_token_invalid_id(setup_database):  # pylint: disable=unused-argument
    result = revoke_access_token(999)
    assert result is False
