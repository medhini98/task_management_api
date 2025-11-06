# models_attachment.py
from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

class AttachmentOut(BaseModel):
    id: UUID
    task_id: UUID
    filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PresignUploadRequest(BaseModel):
    filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None

class PresignUploadResponse(BaseModel):
    attachment_id: UUID
    key: str
    upload_url: str
    fields: Dict = Field(default_factory=dict)
    method: str = "POST"

class PresignDownloadResponse(BaseModel):
    url: str
    expires_in: int