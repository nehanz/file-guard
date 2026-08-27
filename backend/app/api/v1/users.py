from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import Provide, inject
from app.schemas.user import UserResponse, UserUpdate, UserAdminUpdate, UserListResponse
from app.services.user import UserService
from app.dependencies.container import Container
from app.dependencies.auth import get_current_user, get_current_active_admin
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.put("/me", response_model=UserResponse)
@inject
async def update_users_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(Provide[Container.user_service])
):
    """Update current user profile (wallet, avatar, etc)."""
    return await user_service.update_user(str(current_user.id), update_data, str(current_user.id))

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_users_me(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(Provide[Container.user_service])
):
    """Delete current user profile (soft delete)."""
    await user_service.delete_user(str(current_user.id), str(current_user.id))


# --- Admin Routes ---

@router.get("", response_model=UserListResponse, dependencies=[Depends(get_current_active_admin)])
@inject
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by username or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    user_service: UserService = Depends(Provide[Container.user_service])
):
    """Admin: Get list of users with pagination, searching, and filtering."""
    skip = (page - 1) * size
    users, total = await user_service.get_users(skip=skip, limit=size, search=search, role=role)
    
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        size=size
    )

@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(get_current_active_admin)])
@inject
async def get_user(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service])
):
    """Admin: Get user details by ID."""
    return await user_service.get_user_by_id(user_id)

@router.put("/{user_id}", response_model=UserResponse)
@inject
async def admin_update_user(
    user_id: str,
    update_data: UserAdminUpdate,
    current_user: User = Depends(get_current_active_admin),
    user_service: UserService = Depends(Provide[Container.user_service])
):
    """Admin: Update user profile including role and status."""
    return await user_service.update_user(user_id, update_data, str(current_user.id))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def admin_delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_admin),
    user_service: UserService = Depends(Provide[Container.user_service])
):
    """Admin: Soft delete a user."""
    await user_service.delete_user(user_id, str(current_user.id))
