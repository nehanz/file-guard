from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.file import FileRecord
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository[FileRecord]):
    """File repository."""
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "files", FileRecord)

    async def get_by_hash(self, file_hash: str) -> FileRecord | None:
        return await self.get_by_field("file_hash", file_hash)

    async def get_user_files(self, user_id: str | ObjectId, skip: int = 0, limit: int = 100) -> tuple[list[FileRecord], int]:
        filters = {"user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id}
        return await self.list(skip=skip, limit=limit, filters=filters)
