import re
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    wallet_address: Optional[str] = None

    @field_validator("password")
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    @field_validator("wallet_address")
    def validate_wallet_address(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^0x[a-fA-F0-9]{40}$", v):
            raise ValueError("Invalid blockchain wallet address format")
        return v


class UserResponse(UserBase):
    id: str
    is_active: bool
    role: str
    wallet_address: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_str(cls, v: Any) -> str:
        return str(v) if v is not None else ""


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    wallet_address: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @field_validator("wallet_address")
    def validate_wallet_address(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^0x[a-fA-F0-9]{40}$", v):
            raise ValueError("Invalid blockchain wallet address format")
        return v


class UserAdminUpdate(UserUpdate):
    is_active: Optional[bool] = None
    role: Optional[str] = None
    is_superuser: Optional[bool] = None


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    size: int


class UserLogin(BaseModel):
    username: Optional[str] = Field(None, description="Username or Email")
    email: Optional[str] = Field(None, description="Email address")
    password: str

    @model_validator(mode="before")
    @classmethod
    def normalize_login_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if not values.get("username") and values.get("email"):
                values["username"] = values["email"]
        return values


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
