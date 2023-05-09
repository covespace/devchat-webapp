# management.py
from webapp.database import Session
from webapp.models import Organization


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
    organization = Organization(name=name, country_code=country_code)

    try:
        session.add(organization)
        session.commit()
        session.refresh(organization)  # Refresh to get the latest state from the database
        session.expunge(organization)  # Detach the object from the session
        return organization
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()
