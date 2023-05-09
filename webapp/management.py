# management.py
from webapp.database import Session
from webapp.models import Organization
from webapp.utils import generate_uuid


def create_organization(name: str, country_code: str) -> Organization:
    """
    Create a new organization.

    Args:
        name (str): Name of the organization
        country_code (str): Location of the organization

    Returns:
        Organization: The created organization object
    """
    session = Session()
    organization = Organization(uuid=generate_uuid(name), name=name,
                                country_code=country_code)

    try:
        session.add(organization)
        session.commit()
        return organization
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()
