from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.files import router as files_router
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router, prefix=settings.AUTH_ENDPOINT, tags=["Authentication"])
api_router.include_router(users_router, prefix=settings.USERS_ENDPOINT, tags=["Users"])
api_router.include_router(files_router, prefix=settings.FILES_ENDPOINT, tags=["Files"])
