from typing import List

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from webapp.controller import create_organization
from webapp.controller import get_users_of_organization
from webapp.dependencies import get_db

router = APIRouter()


class CreateOrgRequest(BaseModel):
    name: str
    country_code: str


class CreateOrgResponse(BaseModel):
    message: str
    org_id: int


@router.post("/organizations", response_model=CreateOrgResponse, status_code=201)
async def create_organization_endpoint(org: CreateOrgRequest, db: Session = Depends(get_db)):
    """
    Create a new organization.

    Args:
        org (CreateOrgRequest): The organization data to create.

    Returns:
        CreateOrgResponse: The created organization object.
    """
    org = create_organization(db, org.name, org.country_code)
    return CreateOrgResponse(message="Organization created successfully.", org_id=org.id)


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str


@router.get("/organizations/{organization_id}/users", response_model=List[UserResponse])
async def list_users_endpoint(
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
