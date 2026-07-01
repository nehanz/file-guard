from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.log import VerificationLog, ActivityLog
from app.repositories.base import BaseRepository


class VerificationLogRepository(BaseRepository[VerificationLog]):
    """Verification log repository."""
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "verification_logs", VerificationLog)

    async def get_by_file_id(self, file_id: str | ObjectId, skip: int = 0, limit: int = 50) -> tuple[list[VerificationLog], int]:
        filters = {"file_id": ObjectId(file_id) if isinstance(file_id, str) else file_id}
        return await self.list(skip=skip, limit=limit, filters=filters, sort_by="created_at", sort_order=-1)


class ActivityLogRepository(BaseRepository[ActivityLog]):
    """Activity log repository."""
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "activity_logs", ActivityLog)

    async def get_by_user_id(self, user_id: str | ObjectId, skip: int = 0, limit: int = 50) -> tuple[list[ActivityLog], int]:
        filters = {"user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id}
        return await self.list(skip=skip, limit=limit, filters=filters, sort_by="created_at", sort_order=-1)
