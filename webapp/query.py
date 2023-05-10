"""
query.py contains functions to query the database.
"""
from datetime import datetime
from typing import List
from webapp.database import Session
from webapp.models import Organization, User, organization_user
from webapp.models import AccessToken


def get_users_of_organization(organization_id: int, columns: List[str] = None) -> List[list]:
    """
    Get all users of an organization.

    Args:
        organization_id (int): Unique ID of the organization
        columns (list, optional): List of columns to return. Default is ['id', 'username', 'email'].

    Returns:
        list: List of lists containing user information.
            Each inner list contains user data in the same order as the input or default columns.
    """
    if columns is None:
        columns = ['id', 'username', 'email']

    session = Session()
    users = session.query(User).with_entities(*[getattr(User, column) for column in columns]).\
        join(organization_user).\
        join(Organization).\
        filter(Organization.id == organization_id).all()
    result = [list(user) for user in users]

    session.close()
    return result


def get_valid_tokens_of_organization(organization_id: int) -> List[AccessToken]:
    """
    Get all valid tokens' information of an organization.

    Args:
        organization_id (int): Unique ID of the organization

    Returns:
        list: List of AccessToken objects containing valid tokens' information.
    """
    session = Session()
    valid_tokens = session.query(AccessToken).\
        join(Organization).\
        filter(Organization.id == organization_id,
               AccessToken.revoke_time == None).all()  # pylint: disable=C0121

    session.close()
    return valid_tokens


def get_revoked_token_hashes(start_time: datetime, end_time: datetime) -> List[str]:
    """
    Get revoked tokens that were revoked within the specified time range [start_time, end_time).

    Args:
        start_time (datetime): Start time of the time range
        end_time (datetime): End time of the time range

    Returns:
        list: List of token hashes of revoked tokens within the specified time range.
    """
    session = Session()
    revoked_tokens = session.query(AccessToken.token_hash).\
        filter(AccessToken.revoke_time >= start_time, AccessToken.revoke_time < end_time).all()

    session.close()
    return [token_hash[0] for token_hash in revoked_tokens]
