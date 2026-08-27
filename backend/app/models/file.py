from typing import Dict, Any, Optional
from pydantic import Field
from app.models.base import BaseDBModel, PyObjectId


class FileRecord(BaseDBModel):
    """File record database model for tracking file integrity."""
    user_id: PyObjectId
    filename: str
    original_size: int
    content_type: str
    file_hash: str = Field(..., description="SHA-256 hash of the file")
    storage_path: Optional[str] = None
    blockchain_tx_id: Optional[str] = Field(default=None, description="Transaction ID if anchored to blockchain")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending", description="Status: pending, anchored, verified, compromised")
