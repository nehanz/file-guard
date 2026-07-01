from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from dependency_injector.wiring import Provide, inject
from app.schemas.user import UserCreate, UserResponse, Token, ChangePassword, UserLogin
from app.services.auth import AuthService
from app.dependencies.container import Container
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """Register a new user."""
    return await auth_service.register_user(user_in)

@router.post("/login", response_model=Token)
@inject
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """Authenticate user and return tokens (supports form login for Swagger UI)."""
    login_data = UserLogin(username=form_data.username, password=form_data.password)
    return await auth_service.authenticate_user(login_data, request)

@router.post("/refresh", response_model=Token)
@inject
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """Refresh access token."""
    return await auth_service.refresh_token(refresh_token)

@router.post("/logout")
@inject
async def logout(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """Logout user by revoking refresh tokens."""
    await auth_service.logout(str(current_user.id))
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current logged in user."""
    return current_user

@router.post("/change-password")
@inject
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """Change user password."""
    await auth_service.change_password(str(current_user.id), password_data)
    return {"message": "Password updated successfully"}
