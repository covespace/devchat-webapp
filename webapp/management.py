"""
management.py contains functions to create and update data in the database.
"""
import datetime
from webapp.database import Session
from webapp.models import Organization, User
from webapp.models import AccessToken


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


def create_user(username: str, email: str,
                company: str = None, location: str = None, social_profile: str = None) -> User:
    """
    Create a new user.

    Args:
        username (str): Unique username of the user
        email (str): Primary email of the user
        company (str, optional): Company the user is associated with
        location (str, optional): Location of the user
        social_profile (str, optional): Link to the user's social profile

    Returns:
        User: The created user object
    """
    session = Session()
    user = User(username=username, email=email,
                company=company, location=location, social_profile=social_profile)

    try:
        session.add(user)
        session.commit()
        session.refresh(user)  # Refresh to get the latest state from the database
        session.expunge(user)  # Detach the object from the session
        return user
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()


def add_user_to_organization(user_id: int, organization_id: int) -> bool:
    """
    Add an existing user to an organization.

    Args:
        user_id (int): Unique ID of the user
        organization_id (int): Unique ID of the organization

    Returns:
        bool: True if the user was added successfully, False otherwise
    """
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    organization = session.query(Organization).filter(Organization.id == organization_id).first()

    if user and organization:
        organization.users.append(user)
        try:
            session.commit()
            return True
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()
    else:
        return False


def create_token(user_id: int, organization_id: int, name: str, region: str = None) -> AccessToken:
    """
    Create a new access token for a user.

    Args:
        user_id (int): Unique ID of the user
        organization_id (int): Unique ID of the organization
        name (str): Name of the token
        region (str, optional): Region of the target service as the prefix of a token

    Returns:
        AccessToken: The created access token object
    """
    if region is not None:
        if len(region) < 2 or len(region) > 4:
            raise ValueError("Region must be 2 to 4 characters.")

    session = Session()
    token = AccessToken(user_id=user_id, organization_id=organization_id, name=name, region=region)

    try:
        session.add(token)
        session.commit()
        session.refresh(token)  # Refresh to get the latest state from the database
        session.expunge(token)  # Detach the object from the session
        return token
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()


def revoke_token(token_id: int) -> bool:
    """
    Revoke an access token by setting its revoke_time.

    Args:
        token_id (int): Unique ID of the access token

    Returns:
        bool: True if the token was revoked successfully, False otherwise
    """
    session = Session()
    token = session.query(AccessToken).filter(AccessToken.id == token_id).first()

    if token:
        token.revoke_time = datetime.datetime.utcnow()
        try:
            session.commit()
            return True
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()
    else:
        return False
