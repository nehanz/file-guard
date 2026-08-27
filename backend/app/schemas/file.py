from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

class FileMetadata(BaseModel):
    extension: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)

class FileResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    original_size: int
    content_type: str
    file_hash: str
    status: str
    metadata: Dict[str, Any]
    created_at: datetime
    blockchain_tx_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", "user_id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        return str(v) if v is not None else ""

class FileListResponse(BaseModel):
    items: list[FileResponse]
    total: int
    page: int
    size: int
