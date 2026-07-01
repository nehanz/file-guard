from enum import Enum
from typing import List, Optional
from pydantic import EmailStr, Field
from app.models.base import BaseDBModel


class Permission(str, Enum):
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    DELETE_FILES = "delete_files"
    ADMIN_PANEL = "admin_panel"


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class User(BaseDBModel):
    """User database model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    role: Role = Field(default=Role.USER)
    permissions: List[Permission] = Field(default_factory=list)
    wallet_address: Optional[str] = None
