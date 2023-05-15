"""
management.py contains functions to create and update data in the database.
"""
from sqlalchemy.orm import Session
from webapp.model import Organization, User
from webapp.model import AccessKey
from webapp.utils import now


def create_organization(db: Session, name: str, country_code: str) -> Organization:
    """
    Create a new organization.

    Args:
        name (str): Name of the organization
        country_code (str): Location of the organization

    Returns:
        Organization: The created organization object
    """
    organization = Organization(db, name=name, country_code=country_code)

    try:
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization
    except Exception as exc:
        db.rollback()
        raise exc


def create_user(db: Session, username: str, email: str,
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
    user = User(db, username=username, email=email,
                company=company, location=location, social_profile=social_profile)

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as exc:
        db.rollback()
        raise exc


def add_user_to_organization(db: Session, user_id: int, organization_id: int) -> bool:
    """
    Add an existing user to an organization.

    Args:
        user_id (int): Unique ID of the user
        organization_id (int): Unique ID of the organization

    Returns:
        bool: True if the user was added successfully, False otherwise
    """
    user = db.query(User).filter(User.id == user_id).first()
    organization = db.query(Organization).filter(Organization.id == organization_id).first()

    if user and organization:
        organization.users.append(user)
        try:
            db.commit()
            return True
        except Exception as exc:
            db.rollback()
            raise exc
    else:
        return False


def create_access_key(db: Session, user_id: int, organization_id: int,
                      name: str, region: str = None) -> AccessKey:
    """
    Create a new access key for a user.

    Args:
        user_id (int): Unique ID of the user
        organization_id (int): Unique ID of the organization
        name (str): Name of the key
        region (str, optional): Region of the target service as the prefix of a key

    Returns:
        AccessKey: The created access key object
    """
    if region is not None:
        if len(region) < 2 or len(region) > 4:
            raise ValueError("Region must be 2 to 4 characters.")

    key = AccessKey(user_id=user_id, organization_id=organization_id, name=name, region=region)

    try:
        db.add(key)
        db.commit()
        db.refresh(key)
        return key
    except Exception as exc:
        db.rollback()
        raise exc


def revoke_access_key(db: Session, key_id: int) -> bool:
    """
    Revoke an access key by setting its revoke_time.

    Args:
        key_id (int): Unique ID of the access key

    Returns:
        bool: True if the key was revoked successfully, False otherwise
    """
    key = db.query(AccessKey).filter(AccessKey.id == key_id).first()

    if key:
        key.revoke_time = now(db)
        try:
            db.commit()
            return True
        except Exception as exc:
            db.rollback()
            raise exc
    else:
        return False
