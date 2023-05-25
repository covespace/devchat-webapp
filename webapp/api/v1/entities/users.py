from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from webapp.controller import create_user
from webapp.dependencies import get_db
from webapp.api.v1.error import ErrorResponse

router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    email: str


class CreateUserResponse(BaseModel):
    message: str
    user_id: int


@router.post("/users", response_model=CreateUserResponse, status_code=201,
             responses={400: {"model": ErrorResponse}})
async def create_user_endpoint(user: CreateUserRequest, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user (CreateUserRequest): The user data to create.

    Returns:
        CreateUserResponse: The created user object.
    """
    try:
        user = create_user(db, user.username, user.email)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return CreateUserResponse(message="User created successfully.", user_id=user.id)
