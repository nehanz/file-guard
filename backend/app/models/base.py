from datetime import datetime, timezone
from typing import Annotated, Any, Optional
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from bson import ObjectId


def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


# Pydantic v2 custom type for ObjectId
PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]


class BaseDBModel(BaseModel):
    """Base Pydantic model for MongoDB documents."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
