from fastapi import APIRouter

from .organizations import router as organizations_router
from .users import router as users_router

router = APIRouter()

router.include_router(organizations_router)
router.include_router(users_router)
