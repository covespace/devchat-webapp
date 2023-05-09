"""
query.py contains functions to query the database.
"""
from typing import List
from webapp.database import Session
from webapp.models import Organization, User, organization_user


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
