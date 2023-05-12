from fastapi import APIRouter

from api.endpoints import ping

api_router = APIRouter()

api_router.include_router(ping.router, prefix="", tags=[""])
