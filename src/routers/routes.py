from fastapi import APIRouter

from src.routers.auth_routes import auth_router
from src.routers.user_routes import user_router

router = APIRouter(prefix="/comepass/api/v1", tags=["Api V1"])

# Include user routes
router.include_router(user_router)
router.include_router(auth_router)
