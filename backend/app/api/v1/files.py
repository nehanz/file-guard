from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, status
from dependency_injector.wiring import Provide, inject
from app.schemas.file import FileResponse, FileListResponse
from app.services.file import FileService
from app.dependencies.container import Container
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
@inject
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(Provide[Container.file_service])
):
    """Upload a file securely. Streams data, validates size/extension, calculates SHA256 and guards against duplicates."""
    return await file_service.upload_file(str(current_user.id), file)


@router.get("", response_model=FileListResponse)
@inject
async def list_files(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by filename"),
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(Provide[Container.file_service])
):
    """List paginated files uploaded by the current user."""
    skip = (page - 1) * size
    files, total = await file_service.get_files(str(current_user.id), skip=skip, limit=size, search=search)
    
    return FileListResponse(
        items=files,
        total=total,
        page=page,
        size=size
    )

@router.get("/{file_id}", response_model=FileResponse)
@inject
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(Provide[Container.file_service])
):
    """Retrieve details of a specific file."""
    return await file_service.get_file_by_id(str(current_user.id), file_id)

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(Provide[Container.file_service])
):
    """Soft delete a file record and cleanly destroy local storage."""
    await file_service.delete_file(str(current_user.id), file_id)


@router.post("/{file_id}/verify", status_code=status.HTTP_200_OK)
@inject
async def verify_file_integrity(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(Provide[Container.file_service])
):
    """
    Verify file integrity by comparing current hash with:
    1. Database-stored hash
    2. Blockchain-anchored hash (if available)

    Returns verification result with blockchain timestamp and owner if anchored.
    """
    return await file_service.verify_file_integrity(str(current_user.id), file_id)
