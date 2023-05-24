from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Body, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from webapp.controller import create_organization
from webapp.controller import get_users_of_organization
from webapp.dependencies import get_db

router = APIRouter()


class OrganizationResponse(BaseModel):
    id: int
    name: str
    balance: float
    currency: str
    country_code: str
    create_time: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    company: str
    location: str
    social_profile: str
    create_time: datetime

    class Config:
        orm_mode = True


@router.post("/organizations", response_model=OrganizationResponse)
async def create_org(name: str = Body(...), country_code: str = Body(...),
                     db: Session = Depends(get_db)):
    """
    Create a new organization.

    Args:
        name (str): Name of the organization.
        country_code (str): Country code of the organization.

    Returns:
        OrganizationResponse: The created organization object.
    """
    return create_organization(db, name, country_code)


@router.get("/{organization_id}/users", response_model=List[UserResponse])
async def list_users(
        organization_id: int = Path(..., description="ID of the organization to list users for"),
        db: Session = Depends(get_db)):
    """
    List all users of an organization.

    Args:
        organization_id (int): The ID of the organization.

    Returns:
        List[UserResponse]: A list of users belonging to the organization.
    """
    return get_users_of_organization(db, organization_id)
