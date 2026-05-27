import os
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, File
from PIL import Image, UnidentifiedImageError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import rate_limit
from app.core.config import settings
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/files", tags=["files"])


_ALLOWED_FOLDERS = {"avatars", "meals", "progress"}

_PIL_FORMAT_TO_EXT = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
    "GIF": "gif",
}


def _delete_previous_avatar(user: User) -> None:
    if not user.avatar_url:
        return
    if not user.avatar_url.startswith("/uploads/"):
        return
    upload_root = os.path.realpath(settings.UPLOAD_DIR)
    relative = user.avatar_url[len("/uploads/"):]
    target = os.path.realpath(os.path.join(upload_root, relative))
    if not target.startswith(upload_root + os.sep):
        return
    try:
        os.remove(target)
    except OSError:
        pass


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    folder: str = Form("avatars"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Generic image upload endpoint.

    Frontend calls POST /files/upload with multipart form data:
      - file: image (jpg/png/webp/gif), magic bytes verified server-side
      - folder: one of avatars, meals, progress

    Server re-encodes images through Pillow to strip exploits and align the
    extension with the actual format. Returns {url, filename, content_type, size}.
    """
    await rate_limit.enforce(
        request,
        bucket="files-upload",
        limit=20,
        window_seconds=300,
        extra=str(user.id),
    )

    if folder not in _ALLOWED_FOLDERS:
        raise HTTPException(400, f"Invalid folder. Allowed: {sorted(_ALLOWED_FOLDERS)}")

    content = await file.read()
    file_size = len(content)

    if file_size <= 0:
        raise HTTPException(400, "Empty file")
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, "File too large")

    try:
        with Image.open(BytesIO(content)) as img:
            img.verify()
        with Image.open(BytesIO(content)) as img:
            pil_format = (img.format or "").upper()
            normalized = img.convert("RGB" if pil_format in {"JPEG", "JPG"} else "RGBA" if pil_format == "PNG" else img.mode)
            buf = BytesIO()
            save_format = "JPEG" if pil_format in {"JPEG", "JPG"} else pil_format if pil_format in {"PNG", "WEBP", "GIF"} else "JPEG"
            save_kwargs: dict = {"format": save_format}
            if save_format == "JPEG":
                save_kwargs["quality"] = 90
            normalized.save(buf, **save_kwargs)
            normalized_bytes = buf.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        raise HTTPException(400, "Invalid image")

    ext = _PIL_FORMAT_TO_EXT.get(save_format, "jpg")
    content_type = f"image/{'jpeg' if ext == 'jpg' else ext}"
    original_filename = file.filename or f"upload.{ext}"

    relative_path = f"{folder}/{user.id}/{uuid.uuid4()}.{ext}"
    upload_root = os.path.realpath(settings.UPLOAD_DIR)
    filepath = os.path.realpath(os.path.join(upload_root, relative_path))
    if not filepath.startswith(upload_root + os.sep):
        raise HTTPException(400, "Invalid path")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(normalized_bytes)

    url = f"/uploads/{relative_path}"

    if folder == "avatars":
        _delete_previous_avatar(user)
        user.avatar_url = url

    return {
        "url": url,
        "filename": original_filename,
        "content_type": content_type,
        "size": len(normalized_bytes),
    }
