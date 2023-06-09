import os
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from webapp.controller import create_user, create_organization, add_user_to_organization
from webapp.controller import create_access_key
from webapp.controller.query import login_by_key, get_user_profile
from webapp.controller.query import get_organizations_of_user, get_user_keys_in_organizations
from webapp.dependencies import get_db
from webapp.utils import send_email, verify_hcaptcha, get_logger

logger = get_logger(__name__)
router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    email: str
    token: str


class CreateUserResponse(BaseModel):
    user_id: int


@router.post("/users", response_model=CreateUserResponse, status_code=201)
async def create_user_endpoint(user_req: CreateUserRequest, db: Session = Depends(get_db)):
    if not verify_hcaptcha(user_req.token):
        raise HTTPException(status_code=401,
                            detail="Invalid hCaptcha token. Please refresh the page and try again.")
    template_id = os.getenv("SENDGRID_TEMPLATE_ID")
    if not template_id:
        logger.error("SENDGRID_TEMPLATE_ID environment variable is not set")
        raise HTTPException(status_code=500,
                            detail="Email server error. Please contact hello@devchat.ai.")
    try:
        user = create_user(db, user_req.username, user_req.email)
        org = create_organization(db, user.username)
        add_user_to_organization(db, user.id, org.id, 'owner')
        _, value = create_access_key(db, user.id, org.id)
        status = send_email(from_address="hello@devchat.ai", from_name="DevChat Team",
                            to_address=user.email,
                            template_id=template_id,
                            template_data={"user_name": user.username, "access_key": value})
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as exc:
        logger.exception("Unknown error creating user %s: %s", user_req.username, str(exc))
        raise HTTPException(status_code=500, detail="Unknown server error.") from exc

    if status != 202:
        raise HTTPException(status_code=status, detail="Failed to send email.")

    return CreateUserResponse(user_id=user.id)


class LoginRequest(BaseModel):
    key: str


class LoginResponse(BaseModel):
    message: str
    user_id: int


@router.post("/login", response_model=LoginResponse)
async def login_endpoint(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user_id = login_by_key(db, request.key)
    except Exception as exc:
        logger.exception("Unknown login error: %s", str(exc))
        raise HTTPException(status_code=500, detail="Unknown server error.") from exc
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid key hash.")
    return LoginResponse(message="Login successful.", user_id=user_id)


class UserProfileResponse(BaseModel):
    username: str
    email: str


@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile_endpoint(user_id: int, db: Session = Depends(get_db)):
    try:
        user_profile = get_user_profile(db, user_id)
    except Exception as exc:
        logger.exception("Unknown error getting profile of user %d: %s", user_id, str(exc))
        raise HTTPException(status_code=500, detail="Unknown server error.") from exc
    if user_profile is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserProfileResponse(**user_profile)


class OrganizationResponse(BaseModel):
    org_id: int
    org_name: str
    role: str
    keys: List[Dict[str, Any]]


@router.get("/users/{user_id}/organizations", response_model=list[OrganizationResponse])
async def get_user_organizations_endpoint(user_id: int, db: Session = Depends(get_db)):
    try:
        organizations = get_organizations_of_user(db, user_id)
        org_ids = [org["id"] for org in organizations]
        org_keys = get_user_keys_in_organizations(db, user_id, org_ids)

        for org in organizations:
            org["org_id"] = org.pop("id")
            org["org_name"] = org.pop("name")
            org["keys"] = org_keys.get(org["org_id"], [])
    except Exception as exc:
        logger.exception("Unknown error getting organizations of user %d: %s", user_id, str(exc))
        raise HTTPException(status_code=500, detail="Unknown server error.") from exc

    return [OrganizationResponse(**org) for org in organizations]
