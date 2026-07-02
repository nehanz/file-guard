from typing import Any, Dict, Optional
from bson import ObjectId
from app.core.exceptions import AppException, NotFoundException, ValidationException
from app.models.user import User
from app.models.log import ActivityLog
from app.repositories.user import UserRepository
from app.repositories.log import ActivityLogRepository
from app.schemas.user import UserUpdate, UserAdminUpdate


class UserService:
    def __init__(self, user_repo: UserRepository, activity_log_repo: ActivityLogRepository):
        self.user_repo = user_repo
        self.activity_log_repo = activity_log_repo

    async def _log_activity(self, user_id: str | ObjectId, action: str, details: Dict[str, Any] = None):
        """Helper to create audit logs."""
        await self.activity_log_repo.create(ActivityLog(
            user_id=user_id,
            action=action,
            entity_type="user",
            entity_id=user_id,
            details=details or {}
        ))

    async def get_users(self, skip: int = 0, limit: int = 10, search: Optional[str] = None, role: Optional[str] = None) -> tuple[list[User], int]:
        filters = {}
        if search:
            filters["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        if role:
            filters["role"] = role

        return await self.user_repo.list(skip=skip, limit=limit, filters=filters, sort_by="created_at", sort_order=-1)

    async def get_user_by_id(self, user_id: str) -> User:
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def update_user(self, user_id: str, update_data: UserUpdate | UserAdminUpdate, current_user_id: str) -> User:
        user = await self.get_user_by_id(user_id)
        
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return user

        # Check for duplicates if email or username is updated
        if "email" in update_dict and update_dict["email"] != user.email:
            existing = await self.user_repo.get_by_email(update_dict["email"])
            if existing:
                raise ValidationException("Email already taken")
                
        if "username" in update_dict and update_dict["username"] != user.username:
            existing = await self.user_repo.get_by_username(update_dict["username"])
            if existing:
                raise ValidationException("Username already taken")

        updated_user = await self.user_repo.update(user_id, update_dict)
        
        # Audit log
        await self._log_activity(
            current_user_id, 
            "update_profile" if str(user_id) == str(current_user_id) else "admin_update_user",
            {"updated_fields": list(update_dict.keys()), "target_user": str(user_id)}
        )

        return updated_user

    async def delete_user(self, user_id: str, current_user_id: str) -> None:
        user = await self.get_user_by_id(user_id)
        
        # Soft delete is the default in repository
        deleted = await self.user_repo.delete(user_id)
        if not deleted:
            raise AppException("Failed to delete user")
            
        # Audit log
        await self._log_activity(
            current_user_id, 
            "delete_profile" if str(user_id) == str(current_user_id) else "admin_delete_user",
            {"target_user": str(user_id)}
        )
