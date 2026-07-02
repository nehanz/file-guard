import os
import uuid
import hashlib
import aiofiles
from typing import Optional
from fastapi import UploadFile
from bson import ObjectId

from app.core.config import settings
from app.core.exceptions import ValidationException, AppException, NotFoundException
from app.models.file import FileRecord
from app.models.log import ActivityLog
from app.repositories.file import FileRepository
from app.repositories.log import ActivityLogRepository
from app.utils.file_utils import get_file_extension, ensure_upload_dir_exists

class FileService:
    def __init__(self, file_repo: FileRepository, activity_log_repo: ActivityLogRepository):
        self.file_repo = file_repo
        self.activity_log_repo = activity_log_repo
        ensure_upload_dir_exists(settings.UPLOAD_DIR)

    async def _log_activity(self, user_id: str | ObjectId, action: str, entity_id: str | ObjectId, details: dict = None):
        await self.activity_log_repo.create(ActivityLog(
            user_id=user_id,
            action=action,
            entity_type="file",
            entity_id=entity_id,
            details=details or {}
        ))

    async def upload_file(self, user_id: str, file: UploadFile) -> FileRecord:
        # Validate Extension
        ext = get_file_extension(file.filename)
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise ValidationException(f"File extension {ext} not allowed.")

        # Streaming upload and hashing
        unique_filename = f"{uuid.uuid4()}{ext}"
        storage_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        sha256_hash = hashlib.sha256()
        file_size = 0
        
        try:
            async with aiofiles.open(storage_path, 'wb') as out_file:
                while content := await file.read(65536):  # 64kb chunks
                    file_size += len(content)
                    if file_size > settings.MAX_UPLOAD_SIZE:
                        os.remove(storage_path)
                        raise ValidationException(f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024):.0f} MB")
                        
                    sha256_hash.update(content)
                    await out_file.write(content)
        except Exception as e:
            if os.path.exists(storage_path):
                os.remove(storage_path)
            raise AppException(f"Failed to process file upload: {str(e)}")
            
        file_hash_hex = sha256_hash.hexdigest()

        # Check for duplicates across system
        existing_file = await self.file_repo.get_by_hash(file_hash_hex)
        if existing_file:
            os.remove(storage_path)
            raise ValidationException(f"File with hash {file_hash_hex} already exists in the system.")

        # Create Record
        file_record = await self.file_repo.create(FileRecord(
            user_id=user_id,
            filename=file.filename,
            original_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            file_hash=file_hash_hex,
            storage_path=storage_path,
            metadata={"extension": ext}
        ))

        # Log Activity
        await self._log_activity(user_id, "file_upload", file_record.id, {"filename": file.filename, "size": file_size, "hash": file_hash_hex})

        return file_record

    async def get_files(self, user_id: str, skip: int = 0, limit: int = 10, search: Optional[str] = None) -> tuple[list[FileRecord], int]:
        filters = {"user_id": ObjectId(user_id)}
        if search:
            filters["filename"] = {"$regex": search, "$options": "i"}

        return await self.file_repo.list(skip=skip, limit=limit, filters=filters, sort_by="created_at", sort_order=-1)

    async def get_file_by_id(self, user_id: str, file_id: str) -> FileRecord:
        file_record = await self.file_repo.get(file_id)
        if not file_record or str(file_record.user_id) != str(user_id):
            raise NotFoundException("File not found")
        return file_record

    async def delete_file(self, user_id: str, file_id: str) -> None:
        file_record = await self.get_file_by_id(user_id, file_id)
        
        # Soft delete the database record
        deleted = await self.file_repo.delete(file_id)
        if not deleted:
            raise AppException("Failed to delete file record")

        # Physically remove the file from temporary storage
        if file_record.storage_path and os.path.exists(file_record.storage_path):
            os.remove(file_record.storage_path)
            
        # Log Activity
        await self._log_activity(user_id, "file_delete", file_id, {"filename": file_record.filename, "hash": file_record.file_hash})
