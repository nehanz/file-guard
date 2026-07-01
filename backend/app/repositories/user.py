from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository."""
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users", User)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_by_field("email", email)

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_by_field("username", username)
