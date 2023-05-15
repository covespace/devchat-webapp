from fastapi import APIRouter

from . import organization
from . import ping

api_router = APIRouter()

api_router.include_router(ping.router, prefix="", tags=[""])
api_router.include_router(organization.router, prefix="", tags=[""])
