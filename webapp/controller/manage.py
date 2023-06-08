"""
management.py contains functions to create and update data in the database.
"""
from typing import Tuple, Optional
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from webapp.model import Organization, User, organization_user, Role
from webapp.model import AccessKey
from webapp.utils import now, generate_access_key
from webapp.utils import get_logger

logger = get_logger(__name__)


def create_organization(db: Session, name: str, country: Optional[str] = None) -> Organization:
    """
    Create a new organization.

    Args:
        name (str): Name of the organization
        country_code (str): Location of the organization

    Returns:
        Organization: The created organization object
    """
    try:
        organization = Organization(db, name=name, country_code=country)
        logger.info("Created organization %d (name: %s)", organization.id, organization.name)
        return organization
    except IntegrityError as error:
        raise ValueError("Organization name already exists.") from error


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
    try:
        user = User(db, username=username, email=email,
                    company=company, location=location, social_profile=social_profile)
        logger.info("Created user %d (username: %s)", user.id, user.username)
        return user
    except IntegrityError as error:
        error_message = str(error.orig)
        if "email" in error_message:
            raise ValueError("Email already exists.") from error
        if "username" in error_message:
            raise ValueError("Username already exists.") from error
        raise error


def add_user_to_organization(db: Session, user_id: int, organization_id: int,
                             role: Optional[str] = 'member') -> bool:
    """
    Add an existing user to an organization.

    Args:
        user_id (int): Unique ID of the user
        organization_id (int): Unique ID of the organization
        role (str): Role to assign to the user

    Returns:
        bool: True if the user was added successfully, False otherwise
    """
    try:
        stmt = insert(organization_user).values(
            organization_id=organization_id,
            user_id=user_id,
            role=Role[role.upper()]
        )
        db.execute(stmt)
        db.commit()
        logger.info("Added user %d to organization %d", user_id, organization_id)
        return True
    except IntegrityError as error:
        db.rollback()
        raise ValueError("Accounts not found or duplicate.") from error
    except Exception as exc:
        db.rollback()
        raise exc


def assign_role_to_user(db: Session, user_id: int, org_id: int, role: Role):
    try:
        db.execute(
            organization_user.update()
            .where(organization_user.c.user_id == user_id)
            .where(organization_user.c.organization_id == org_id)
            .values(role=role)
        )
        db.commit()
        logger.info("Assigned role %s to user %d in organization %d", role, user_id, org_id)
        return True
    except IntegrityError as error:
        db.rollback()
        raise ValueError("No such user or organization.") from error
    except Exception as exc:
        db.rollback()
        raise exc


def create_access_key(db: Session, user_id: int, organization_id: int,
                      name: str = None) -> Tuple[AccessKey, str]:
    """
    Create a new access key for a user.

    Args:
        user_id (int): Unique ID of the user
        organization_id (int): Unique ID of the organization
        name (str): Name of the key

    Returns:
        Tuple[AccessKey, str]: The created access key object and its value
    """
    with db.begin_nested():
        # Check if the user belongs to the organization
        user_org_role = db.query(organization_user).filter(
            organization_user.c.user_id == user_id,
            organization_user.c.organization_id == organization_id).first()
        if not user_org_role:
            raise ValueError("User not found in the organization")

        value = generate_access_key(organization_id)
        key = AccessKey(value, user_id=user_id, organization_id=organization_id, name=name)

        db.add(key)
        db.commit()
    logger.info("Created access key %d (hash: %s) for user %d in organization %d",
                key.id, key.key_hash, key.user_id, key.organization_id)
    return (key, value)


def revoke_access_key(db: Session, key_id: int):
    """
    Revoke an access key by setting its revoke_time.

    Args:
        key_id (int): Unique ID of the access key

    Returns:
        bool: True if the key was revoked successfully, False otherwise
    """
    key = db.query(AccessKey).filter(AccessKey.id == key_id).first()

    if key:
        try:
            key.revoke_time = now(db)
            db.commit()
            logger.info("Revoked access key %d (hash: %s) for user %d in organization %d",
                        key.id, key.key_hash, key.user_id, key.organization_id)
            return True
        except Exception as exc:
            db.rollback()
            raise exc
    else:
        raise ValueError("Key does not exist.")
