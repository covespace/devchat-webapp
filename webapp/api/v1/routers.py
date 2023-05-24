from fastapi import APIRouter

from .entities.routers import router as entities_router
from .transactions.routers import router as transactions_router

router = APIRouter()

router.include_router(entities_router, prefix="/v1")
router.include_router(transactions_router, prefix="/v1")
