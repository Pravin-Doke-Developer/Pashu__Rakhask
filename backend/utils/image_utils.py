import os
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def is_allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def validate_image_file(file_storage, max_size_mb: int = 10) -> tuple[bool, str | None]:
    if file_storage is None:
        return False, 'No image file was uploaded.'

    if file_storage.filename == '':
        return False, 'No image file was uploaded.'

    if not is_allowed_file(file_storage.filename):
        return False, 'Unsupported file type. Please upload JPG, JPEG, PNG, or WEBP.'

    if file_storage.content_length and file_storage.content_length > max_size_mb * 1024 * 1024:
        return False, f'Image exceeds the {max_size_mb}MB upload limit.'

    try:
        file_storage.stream.seek(0)
        image = Image.open(file_storage)
        image.verify()
        file_storage.stream.seek(0)
        image = Image.open(file_storage)
        image.load()
        image_size = image.size
        if image_size[0] <= 0 or image_size[1] <= 0:
            return False, 'The uploaded image is invalid or unreadable.'
    except (UnidentifiedImageError, OSError, ValueError):
        return False, 'The uploaded image is corrupt or unreadable.'

    return True, None


def save_uploaded_image(file_storage, dest_dir: str) -> str:
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    filename = Path(file_storage.filename).name
    final_path = dest_path / filename
    file_storage.save(final_path)
    return str(final_path)
