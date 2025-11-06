# routers/lookup.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app_db.session import get_session
from app_db import models as dbm

router = APIRouter()

@router.get("/users")
def list_users(db: Session = Depends(get_session)):
    return [{"id": u.id, "email": u.email, "name": f"{u.first_name} {u.last_name or ''}".strip()}
            for u in db.query(dbm.User).order_by(dbm.User.email)]

@router.get("/tags")
def list_tags(db: Session = Depends(get_session)):
    return [{"id": t.id, "name": t.name} for t in db.query(dbm.Tag).order_by(dbm.Tag.name)]