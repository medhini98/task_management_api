# routers/attachments.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4, UUID
from core.config import settings
from services.storage import get_storage
from app_db.session import get_session
from app_db import models as dbm
from models_attachment import (
    PresignUploadRequest, PresignUploadResponse,
    AttachmentOut, PresignDownloadResponse
)

router = APIRouter(prefix="/attachments", tags=["attachments"])

def _ensure_task(db: Session, task_id: UUID) -> dbm.Task:
    t = db.get(dbm.Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@router.post("/tasks/{task_id}/presign-upload", response_model=PresignUploadResponse)
def presign_upload(task_id: UUID, body: PresignUploadRequest, db: Session = Depends(get_session)):
    _ensure_task(db, task_id)
    # Build key: attachments/{task_id}/{uuid}.{ext}
    ext = body.filename.rsplit(".", 1)[-1] if "." in body.filename else "bin"
    key = f"{settings.aws_s3_prefix}{task_id}/{uuid4().hex}.{ext}"

    # Insert DB row
    att = dbm.Attachment(
        task_id=task_id,
        uploader_id=None,  # plug your auth user id if available
        filename=body.filename,
        content_type=body.content_type,
        size_bytes=body.size_bytes,
        storage_key=key,
    )
    db.add(att)
    db.commit()
    db.refresh(att)

    storage = get_storage()
    url, fields = storage.presign_upload(key, body.content_type, settings.presigned_expires_seconds)

    return PresignUploadResponse(
        attachment_id=att.id, key=key, upload_url=url, fields=fields, method="POST"
    )

@router.get("/tasks/{task_id}", response_model=List[AttachmentOut])
def list_attachments(task_id: UUID, db: Session = Depends(get_session)):
    _ensure_task(db, task_id)
    q = db.query(dbm.Attachment).filter(dbm.Attachment.task_id == task_id).order_by(dbm.Attachment.created_at.desc())
    return q.all()

@router.get("/{attachment_id}/download-url", response_model=PresignDownloadResponse)
def get_download_url(attachment_id: UUID, db: Session = Depends(get_session)):
    att = db.get(dbm.Attachment, attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    storage = get_storage()
    url = storage.presign_download(att.storage_key, settings.presigned_expires_seconds)
    return PresignDownloadResponse(url=url, expires_in=settings.presigned_expires_seconds)

@router.delete("/{attachment_id}", status_code=204)
def delete_attachment(attachment_id: UUID, db: Session = Depends(get_session)):
    att = db.get(dbm.Attachment, attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found")
    storage = get_storage()
    try:
        storage.delete_object(att.storage_key)
    finally:
        db.delete(att)
        db.commit()
    return

# ---------- Local backend only ----------

@router.post("/tasks/{task_id}/upload-direct")
async def upload_direct(task_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_session)):
    if settings.storage_backend != "local":
        raise HTTPException(status_code=400, detail="upload-direct only for local backend")

    _ensure_task(db, task_id)

    # key naming compatible with S3 path layout
    original_ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
    key = f"{settings.aws_s3_prefix}{task_id}/{uuid4().hex}.{original_ext}"

    storage = get_storage()  # LocalStorage
    # save locally
    storage.save_file(key, file)

    att = dbm.Attachment(
        task_id=task_id,
        uploader_id=None,
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=None,
        storage_key=key,
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return {"attachment_id": str(att.id), "key": key}

@router.get("/local-download")
def local_download(path: str = Query(..., description="Absolute path inside LOCAL_STORAGE_DIR")):
    import os
    from fastapi.responses import FileResponse
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="application/octet-stream", filename=os.path.basename(path))