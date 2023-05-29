from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Body, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from webapp.controller import add_user_to_organization
from webapp.controller import create_access_key
from webapp.controller import create_organization
from webapp.controller import get_users_of_organization
from webapp.controller import get_organization_id_by_name
from webapp.dependencies import get_db
from webapp.model import Role
from webapp.utils import send_email


router = APIRouter()


class CreateOrgRequest(BaseModel):
    name: str
    country_code: Optional[str] = None


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
    try:
        org = create_organization(db, org.name, org.country_code)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return CreateOrgResponse(message="Organization created successfully.", org_id=org.id)


class GetOrgIdByNameResponse(BaseModel):
    org_id: int


@router.get("/organizations/{org_name}/id", response_model=GetOrgIdByNameResponse)
async def get_organization_id_by_name_endpoint(
        org_name: str = Path(..., description="Name of the organization to get the ID for"),
        db: Session = Depends(get_db)):
    """
    Get the organization ID with the given name.

    Args:
        org_name (str): Name of the organization

    Returns:
        GetOrgIdByNameResponse: The organization ID with the given name
    """
    org_id = get_organization_id_by_name(db, org_name)
    if org_id is None:
        raise HTTPException(status_code=404, detail="Organization name not found")
    return GetOrgIdByNameResponse(org_id=org_id)


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str


@router.get("/organizations/{org_id}/users", response_model=List[UserResponse])
async def list_users_endpoint(
        org_id: int = Path(..., description="ID of the organization to list users for"),
        db: Session = Depends(get_db)):
    """
    List all users of an organization.

    Args:
        org_id (int): The ID of the organization.

    Returns:
        List[UserResponse]: A list of users belonging to the organization.
    """
    return get_users_of_organization(db, org_id)


class AddUserRequest(BaseModel):
    user_id: int
    role: str


class AddUserResponse(BaseModel):
    message: str


@router.post("/organizations/{org_id}/users", response_model=AddUserResponse, status_code=200)
async def add_user_to_organization_endpoint(
        org_id: int = Path(..., description="ID of the organization to add the user to"),
        user: AddUserRequest = Body(...),
        db: Session = Depends(get_db)):
    """
    Add a user with a role to an organization.

    Args:
        org_id (int): The ID of the organization.
        user (AddUserRequest): The user data to add.

    Returns:
        AddUserResponse: The result of adding the user to the organization.
    """
    try:
        add_user_to_organization(db, user.user_id, org_id, Role[user.role.upper()])
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AddUserResponse(message="User added to the organization successfully.")


class IssueAccessKeyResponse(BaseModel):
    message: str
    key_hash: str


@router.post("/organizations/{org_id}/user/{user_id}/access_key",
             response_model=IssueAccessKeyResponse, status_code=200)
async def issue_access_key_endpoint(
        org_id: int = Path(..., description="ID of the organization"),
        user_id: int = Path(..., description="ID of the user"),
        db: Session = Depends(get_db)):
    """
    Issue an access key for a user in an organization and send the key to the user by email.

    Args:
        org_id (int): The ID of the organization.
        user_id (int): The ID of the user.

    Returns:
        IssueAccessKeyResponse: The result of issuing the access key.
    """
    try:
        key, value = create_access_key(db, user_id, org_id)
        # Send the access key to the user by email
        status = send_email(from_email="hello@devchat.ai", from_name="DevChat Team",
                            to_email=key.user.email,
                            template_id="d-052755df2d614200b2343aabe018bc22",
                            template_data={"user_name": key.user.email, "access_key": value})
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if status != 202:
        raise HTTPException(status_code=status,
                            detail=f"Failed to send email to {key.user.email}.")
    return IssueAccessKeyResponse(message="Access key issued and sent to the user by email.",
                                  key_hash=key.key_hash)
