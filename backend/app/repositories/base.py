from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone

from app.models.base import BaseDBModel


ModelType = TypeVar("ModelType", bound=BaseDBModel)


class BaseRepository(Generic[ModelType]):
    """
    Base Repository with common CRUD operations and soft delete support.
    """
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model: Type[ModelType]):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[collection_name]
        self.model = model

    async def create(self, obj_in: ModelType | dict) -> ModelType:
        """Create a new document."""
        if isinstance(obj_in, dict):
            document = obj_in.copy()
        else:
            document = obj_in.model_dump(by_alias=True, exclude_unset=True)
            if "_id" in document and document["_id"] is None:
                del document["_id"]

        now = datetime.now(timezone.utc)
        document["created_at"] = now
        document["updated_at"] = now
        document["is_deleted"] = False
        document["deleted_at"] = None

        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return self.model.model_validate(document)

    async def get(self, id: str | ObjectId, include_deleted: bool = False) -> Optional[ModelType]:
        """Get a document by ID."""
        query = {"_id": ObjectId(id) if isinstance(id, str) else id}
        if not include_deleted:
            query["is_deleted"] = False

        document = await self.collection.find_one(query)
        if document:
            return self.model.model_validate(document)
        return None

    async def get_by_field(self, field: str, value: Any, include_deleted: bool = False) -> Optional[ModelType]:
        """Get a document by a specific field."""
        query = {field: value}
        if not include_deleted:
            query["is_deleted"] = False

        document = await self.collection.find_one(query)
        if document:
            return self.model.model_validate(document)
        return None

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_order: int = -1,
        include_deleted: bool = False
    ) -> tuple[List[ModelType], int]:
        """Get a paginated list of documents with optional filtering and sorting."""
        query = filters or {}
        if not include_deleted:
            query["is_deleted"] = False

        cursor = self.collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        total_count = await self.collection.count_documents(query)

        return [self.model.model_validate(doc) for doc in documents], total_count

    async def update(self, id: str | ObjectId, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a document by ID."""
        obj_in["updated_at"] = datetime.now(timezone.utc)
        query = {"_id": ObjectId(id) if isinstance(id, str) else id, "is_deleted": False}
        
        updated_doc = await self.collection.find_one_and_update(
            query,
            {"$set": obj_in},
            return_document=True
        )
        if updated_doc:
            return self.model.model_validate(updated_doc)
        return None

    async def delete(self, id: str | ObjectId, hard_delete: bool = False) -> bool:
        """Delete a document by ID (soft delete by default)."""
        query = {"_id": ObjectId(id) if isinstance(id, str) else id}
        
        if hard_delete:
            result = await self.collection.delete_one(query)
            return result.deleted_count > 0
        
        # Soft delete
        now = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            query,
            {"$set": {"is_deleted": True, "deleted_at": now, "updated_at": now}}
        )
        return result.modified_count > 0
