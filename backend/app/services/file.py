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
from app.blockchain.client import BlockchainClient

class FileService:
    def __init__(self, file_repo: FileRepository, activity_log_repo: ActivityLogRepository, blockchain_client: Optional[BlockchainClient] = None):
        self.file_repo = file_repo
        self.activity_log_repo = activity_log_repo
        self.blockchain_client = blockchain_client
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

        # Anchor hash on blockchain if client is available
        tx_hash = None
        if self.blockchain_client:
            try:
                tx_hash = await self.blockchain_client.store_hash_on_chain(
                    file_id=str(file_record.id),
                    sha256_hash=file_hash_hex
                )
                # Update file record with blockchain transaction hash
                file_record.metadata["blockchain_tx"] = tx_hash
                await self.file_repo.update(str(file_record.id), file_record)
            except Exception as e:
                # Log blockchain error but don't fail the upload
                await self._log_activity(user_id, "blockchain_anchor_failed", file_record.id, {
                    "error": str(e),
                    "hash": file_hash_hex
                })

        # Log Activity
        await self._log_activity(user_id, "file_upload", file_record.id, {
            "filename": file.filename,
            "size": file_size,
            "hash": file_hash_hex,
            "blockchain_tx": tx_hash
        })

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

    async def verify_file_integrity(self, user_id: str, file_id: str) -> dict:
        """
        Verify file integrity by comparing current hash with blockchain-anchored hash.

        Returns:
            dict with verification result and details
        """
        file_record = await self.get_file_by_id(user_id, file_id)

        # Check if file physically exists
        if not os.path.exists(file_record.storage_path):
            raise NotFoundException("File not found in storage")

        # Recalculate current file hash
        sha256_hash = hashlib.sha256()
        async with aiofiles.open(file_record.storage_path, 'rb') as f:
            while chunk := await f.read(65536):
                sha256_hash.update(chunk)

        current_hash = sha256_hash.hexdigest()
        stored_hash = file_record.file_hash

        # Basic database hash verification
        db_match = current_hash == stored_hash

        result = {
            "file_id": str(file_record.id),
            "filename": file_record.filename,
            "current_hash": current_hash,
            "stored_hash": stored_hash,
            "db_integrity_valid": db_match,
            "blockchain_verified": False,
            "blockchain_hash": None,
            "blockchain_timestamp": None,
            "blockchain_owner": None
        }

        # Verify against blockchain if client available
        if self.blockchain_client:
            try:
                # Check if hash exists on blockchain
                exists = await self.blockchain_client.hash_exists(str(file_record.id))

                if exists:
                    # Get blockchain record
                    blockchain_hash, timestamp, owner = await self.blockchain_client.get_hash_from_chain(str(file_record.id))

                    result["blockchain_hash"] = blockchain_hash
                    result["blockchain_timestamp"] = timestamp
                    result["blockchain_owner"] = owner
                    result["blockchain_verified"] = (current_hash == blockchain_hash)
                else:
                    result["blockchain_verified"] = None  # Not anchored

            except Exception as e:
                result["blockchain_error"] = str(e)

        # Log verification activity
        await self._log_activity(user_id, "file_verify", file_id, result)

        return result
