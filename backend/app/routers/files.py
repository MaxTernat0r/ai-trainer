import os
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form("general"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Generic file upload endpoint.

    Frontend calls POST /files/upload with multipart form data:
      - file: the file to upload
      - folder: optional folder name (e.g. 'avatars', 'food')

    Returns {url, filename, content_type, size}.
    """
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, "Invalid file type")

    content = await file.read()
    file_size = len(content)

    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, "File too large")

    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    original_filename = file.filename or f"upload.{ext}"
    unique_filename = f"{folder}/{user.id}/{uuid.uuid4()}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, unique_filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/uploads/{unique_filename}"

    # If this is an avatar upload, also update the user's avatar_url
    if folder == "avatars":
        user.avatar_url = url

    return {
        "url": url,
        "filename": original_filename,
        "content_type": file.content_type or "application/octet-stream",
        "size": file_size,
    }
