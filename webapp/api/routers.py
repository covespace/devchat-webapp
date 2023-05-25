from fastapi import APIRouter
from .v1.routers import router as v1_router
from .jwks import router as jwks_router


router = APIRouter()

router.include_router(v1_router, prefix="/api")
router.include_router(jwks_router, prefix="")
