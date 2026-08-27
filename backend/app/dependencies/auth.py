from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.exceptions import AppException
from app.core.security import decode_token
from app.models.user import User, Role
from app.repositories.user import UserRepository
from app.database.connection import DatabaseConnection
from dependency_injector.wiring import Provide, inject
from app.dependencies.container import Container

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(Provide[Container.user_repo])
) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise AppException("Invalid token type", status_code=401)
        user_id = payload.get("sub")
        if user_id is None:
            raise AppException("Could not validate credentials", status_code=401)
    except Exception as e:
        raise AppException("Could not validate credentials", status_code=401)

    user = await user_repo.get(user_id)
    if user is None:
        raise AppException("User not found", status_code=404)
    if not user.is_active:
        raise AppException("Inactive user", status_code=400)
    return user

async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN and current_user.role != Role.SUPERUSER:
        raise AppException("The user doesn't have enough privileges", status_code=403)
    return current_user
