import os
from fastapi import UploadFile
from datetime import datetime
import shutil
from pathlib import Path

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def get_upload_dir():
    upload_dir = Path(UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    return upload_dir

def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload_file(upload_file: UploadFile, user_id: int) -> str:
    if not is_allowed_file(upload_file.filename):
        raise ValueError("File type not allowed")
    
    if upload_file.content_length and upload_file.content_length > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = upload_file.filename.rsplit(".", 1)[1].lower()
    filename = f"user_{user_id}_{timestamp}.{file_extension}"
    
    # Ensure upload directory exists
    upload_dir = get_upload_dir()
    file_path = upload_dir / filename

    # Save the file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    # Return the relative URL path
    return f"/uploads/{filename}" 