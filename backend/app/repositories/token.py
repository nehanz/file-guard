from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Refresh token repository."""
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "refresh_tokens", RefreshToken)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        return await self.get_by_field("token", token)

    async def revoke_all_for_user(self, user_id: str | ObjectId) -> int:
        """Revoke all tokens for a user."""
        query = {"user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id, "is_revoked": False}
        result = await self.collection.update_many(
            query,
            {"$set": {"is_revoked": True}}
        )
        return result.modified_count
