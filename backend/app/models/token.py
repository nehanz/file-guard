from datetime import datetime
from pydantic import Field
from app.models.base import BaseDBModel, PyObjectId


class RefreshToken(BaseDBModel):
    """Refresh token model for authentication."""
    user_id: PyObjectId
    token: str = Field(...)
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    ip_address: str = Field(default="")
    user_agent: str = Field(default="")
