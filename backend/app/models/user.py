from typing import Optional
from pydantic import EmailStr, Field
from app.models.base import BaseDBModel


class User(BaseDBModel):
    """User database model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    wallet_address: Optional[str] = None
