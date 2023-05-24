from fastapi import APIRouter

from .organization import router as organization_router

router = APIRouter()

router.include_router(organization_router)
