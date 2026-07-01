from typing import Any, Dict, Optional
from pydantic import Field
from app.models.base import BaseDBModel, PyObjectId


class VerificationLog(BaseDBModel):
    """Log entry for file verifications."""
    file_id: PyObjectId
    user_id: PyObjectId
    status: str = Field(..., description="Status of verification: success, failed, compromised")
    hash_verified: str = Field(..., description="The hash calculated during verification")
    details: Dict[str, Any] = Field(default_factory=dict)


class ActivityLog(BaseDBModel):
    """Audit log entry for system activities."""
    user_id: Optional[PyObjectId] = None
    action: str = Field(..., description="Action performed, e.g., login, file_upload, file_verify")
    entity_type: Optional[str] = None
    entity_id: Optional[PyObjectId] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = Field(default="success")
    details: Dict[str, Any] = Field(default_factory=dict)
