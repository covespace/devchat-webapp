from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from webapp.controller import create_organization
from webapp.controller import get_users_of_organization
from webapp.model import Organization, User
from webapp.dependencies import get_db
from pydantic import BaseModel
from datetime import datetime

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
def create_org(name: str = Body(...), country_code: str = Body(...), db: Session = Depends(get_db)):
    return create_organization(db, name, country_code)


@router.get("/{organization_id}/users", response_model=List[UserResponse])
def list_users(organization_id: int, db: Session = Depends(get_db)):
    users = get_users_of_organization(db, organization_id)
    if not users:
        raise HTTPException(status_code=404, detail="Organization not found")
    return users
