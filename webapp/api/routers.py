from fastapi import APIRouter

from . import endpoints

api_router = APIRouter()

api_router.include_router(endpoints.api_router, prefix="/v1", tags=[""])
