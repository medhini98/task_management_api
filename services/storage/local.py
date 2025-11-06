# services/storage/local.py
import os
import shutil
from typing import Optional, Dict, Tuple
from urllib.parse import quote
from fastapi import UploadFile
from core.config import settings

class LocalStorage:
    def __init__(self):
        os.makedirs(settings.local_storage_dir, exist_ok=True)

    def presign_upload(self, key: str, content_type: Optional[str], expires: int) -> Tuple[str, Dict]:
        # Not used directly; we’ll accept the bytes via API in local mode.
        return "", {}

    def save_file(self, key: str, file: UploadFile) -> str:
        # Store file under LOCAL_STORAGE_DIR/{basename}
        basename = key.split("/")[-1]
        path = os.path.join(settings.local_storage_dir, basename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return path

    def presign_download(self, key: str, expires: int) -> str:
        basename = key.split("/")[-1]
        path = os.path.join(settings.local_storage_dir, basename)
        return f"/attachments/local-download?path={quote(path)}"

    def delete_object(self, key: str) -> None:
        basename = key.split("/")[-1]
        path = os.path.join(settings.local_storage_dir, basename)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass