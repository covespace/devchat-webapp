from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from webapp.controller import create_user
from webapp.controller.query import login_by_key_hash, get_user_profile
from webapp.controller.query import get_organizations_of_user, get_user_keys_in_organizations
from webapp.dependencies import get_db


router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    email: str


class CreateUserResponse(BaseModel):
    message: str
    user_id: int


@router.post("/users", response_model=CreateUserResponse, status_code=201)
async def create_user_endpoint(user: CreateUserRequest, db: Session = Depends(get_db)):
    try:
        user = create_user(db, user.username, user.email)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return CreateUserResponse(message="User created successfully.", user_id=user.id)


class LoginRequest(BaseModel):
    key_hash: str


class LoginResponse(BaseModel):
    message: str
    user_id: int


@router.post("/login", response_model=LoginResponse)
async def login_endpoint(request: LoginRequest, db: Session = Depends(get_db)):
    user_id = login_by_key_hash(db, request.key_hash)
    if user_id is not None:
        return LoginResponse(message="Login successful", user_id=user_id)
    else:
        raise HTTPException(status_code=401, detail="Invalid key hash")


class UserProfileResponse(BaseModel):
    username: str
    email: str


@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile_endpoint(user_id: int, db: Session = Depends(get_db)):
    user_profile = get_user_profile(db, user_id)
    if user_profile is not None:
        return UserProfileResponse(**user_profile)
    else:
        raise HTTPException(status_code=404, detail="User not found.")


class OrganizationResponse(BaseModel):
    org_id: int
    org_name: str
    role: str
    keys: List[Dict[str, Any]]


@router.get("/users/{user_id}/organizations", response_model=list[OrganizationResponse])
async def get_user_organizations_endpoint(user_id: int, db: Session = Depends(get_db)):
    organizations = get_organizations_of_user(db, user_id)
    org_ids = [org["id"] for org in organizations]
    org_keys = get_user_keys_in_organizations(db, user_id, org_ids)

    for org in organizations:
        org["org_id"] = org.pop("id")
        org["org_name"] = org.pop("name")
        org["keys"] = org_keys.get(org["org_id"], [])

    return [OrganizationResponse(**org) for org in organizations]
