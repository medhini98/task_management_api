import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central app configuration loaded automatically from `.env`
    using Pydantic v2-compatible BaseSettings.
    """

    # --- Database ---
    database_url: str = "sqlite:////tmp/taskapi.db"  # Lambda writable dir
    #database_url: str  # maps from DATABASE_URL in .env

    # --- Storage configuration ---
    storage_backend: str = "local"  # 'local' or 's3'
    aws_region: str = "ap-south-1"
    aws_s3_bucket: str = "taskapi-medhini-dev"
    aws_s3_prefix: str = "attachments/"
    local_storage_dir: str = "./uploaded_files"
    presigned_expires_seconds: int = 900

    # --- App / environment ---
    environment: str = "dev"
    debug: bool = True
    auto_create_tables: bool = True  # create tables if missing

    # Pydantic settings config
    model_config = SettingsConfigDict(
        env_file=".env",      # auto-load from .env
        env_file_encoding="utf-8",
        extra="ignore"        # ignore unknown .env keys
    )


# Instantiate global settings object
settings = Settings()