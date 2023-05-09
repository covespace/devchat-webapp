# test_management.py
import pytest
from webapp.database import Base, engine, Session, create_tables
from webapp.models import Organization
from webapp.management import create_organization


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
