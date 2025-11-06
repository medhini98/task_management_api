# services/storage/__init__.py
from core.config import settings
from .s3 import S3Storage
from .local import LocalStorage

def get_storage():
    backend = "s3" if settings.storage_backend == "s3" else "local"
    print(f"[storage] using backend: {backend}")
    return S3Storage() if settings.storage_backend == "s3" else LocalStorage()