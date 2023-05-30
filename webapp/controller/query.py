"""
query.py contains functions to query the database.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from webapp.model import Organization, User, organization_user
from webapp.model import AccessKey


def get_organization_id_by_name(db: Session, org_name: str) -> int:
    """
    Get the organization ID with the given name.

    Args:
        org_name (str): Name of the organization

    Returns:
        int: the organization ID with the given name
    """
    org_id = db.query(Organization.id).filter(Organization.name == org_name).first()
    if org_id is None:
        return None
    return org_id[0]


def get_users_of_organization(db: Session, org_id: int,
                              columns: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get all users of an organization.

    Args:
        org_id (int): Unique ID of the organization
        columns (list, optional): List of user columns to return. \
            Default is ['id', 'username', 'email'].

    Returns:
        list: List of dictionaries containing user information. \
            Each dictionary contains user data with keys matching the specified columns.
    """
    if not columns:
        columns = ['id', 'username', 'email']

    users = db.query(User).with_entities(
        *[getattr(User, column).label(column) for column in columns]). \
        join(organization_user). \
        filter(organization_user.c.organization_id == org_id).all()

    return [row._asdict() for row in users]


def get_valid_keys_of_organization(db: Session, organization_id: int) -> List[AccessKey]:
    """
    Get all valid access keys' information of an organization.

    Args:
        organization_id (int): Unique ID of the organization

    Returns:
        list: List of AccessKey objects containing valid keys' information.
    """
    return db.query(AccessKey).join(Organization).filter(
        Organization.id == organization_id,
        AccessKey.revoke_time == None).all()  # pylint: disable=C0121


def get_revoked_key_hashes(db: Session, start_time: datetime, end_time: datetime) -> List[str]:
    """
    Get access keys that were revoked within the specified time range [start_time, end_time).

    Args:
        start_time (datetime): Start time of the time range
        end_time (datetime): End time of the time range

    Returns:
        list: List of key hashes of revoked keys within the specified time range.
    """
    revoked_keys = db.query(AccessKey.key_hash). \
        filter(AccessKey.revoke_time >= start_time, AccessKey.revoke_time < end_time).all()
    return [key_hash[0] for key_hash in revoked_keys]


def get_user_profile(db: Session, user_id: int) -> Optional[Dict[str, str]]:
    user = db.query(User).filter(User.id == user_id).first()
    if user is not None:
        return {"username": user.username, "email": user.email}
    return None


def get_organizations_of_user(db: Session, user_id: int,
                              columns: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get all organizations of a user.

    Args:
        user_id (int): Unique ID of the user
        columns (list, optional): List of organization and organization_user columns to return. \
            Default is ['id', 'name', 'role'].

    Returns:
        list: List of dictionaries containing organization information. \
            Each dictionary contains organization data with keys matching the specified columns.
    """
    if not columns:
        columns = ['id', 'name', 'role']

    selected_columns = []
    for column in columns:
        if hasattr(Organization, column):
            selected_columns.append(getattr(Organization, column).label(column))
        elif hasattr(organization_user.c, column):
            selected_columns.append(getattr(organization_user.c, column).label(column))

    user_orgs = db.query(Organization).with_entities(*selected_columns). \
        join(organization_user). \
        filter(organization_user.c.user_id == user_id).all()

    return [row._asdict() for row in user_orgs]


def get_user_keys_in_organizations(db: Session, user_id: int, org_ids: List[int],
                                   columns: List[str] = None) -> Dict[int, List[Dict[str, Any]]]:
    """
    Get keys of a user in certain organizations.

    Args:
        db (Session): Database session.
        user_id (int): ID of the user.
        org_ids (List[int]): List of organization IDs.
        columns (List[str], optional): List of columns to return. \
            Default is ['id', 'thumbnail', 'create_time'].

    Returns:
        Dict[int, List[Dict[str, Any]]]: Dictionary indexed by organization ID \
            containing a list of dictionaries with key information. \
            Each dictionary contains key data with keys matching the specified columns.
    """
    if not columns:
        columns = ['id', 'thumbnail', 'create_time']
    if 'organization_id' not in columns:
        columns.append('organization_id')
    selected_columns = [getattr(AccessKey, column).label(column) for column in columns]

    user_keys = db.query(AccessKey).with_entities(*selected_columns). \
        filter(AccessKey.user_id == user_id,
               AccessKey.organization_id.in_(org_ids),
               AccessKey.revoke_time.is_(None)).all()

    result = {}
    for row in user_keys:
        row_dict = row._asdict()
        org_id = row_dict.pop('organization_id')
        if org_id not in result:
            result[org_id] = []
        result[org_id].append(row_dict)

    return result
