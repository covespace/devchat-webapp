from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from webapp.controller import create_organization
from webapp.controller import get_users_of_organization
from webapp.model import Organization, User
from webapp.api.dependencies import get_db


router = APIRouter()


@router.post("/", response_model=Organization)
def create_org(name: str, country_code: str, db: Session = Depends(get_db)):
    return create_organization(db, name, country_code)


@router.get("/{organization_id}/users", response_model=List[User])
def list_users(organization_id: int, db: Session = Depends(get_db)):
    users = get_users_of_organization(db, organization_id)
    if not users:
        raise HTTPException(status_code=404, detail="Organization not found")
    return users
