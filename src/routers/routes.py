from fastapi import APIRouter

from src.routers.auth_routes import auth_router
from src.routers.chat_routes import chat_router
from src.routers.perm_routes import perm_router
from src.routers.role_routes import role_router
from src.routers.user_routes import user_router

router = APIRouter()

# Include user routes
router.include_router(user_router)
router.include_router(auth_router)
router.include_router(perm_router)
router.include_router(role_router)
router.include_router(chat_router)
