"""
A session is a unit of work with the DB (handles connection + transaction scope).

In FastAPI we provide a session per request using a dependency so:
    • You always get a fresh, valid session in route handlers
    • It’s closed after the request (no leaks)
    • You can later add transaction wrappers, retries, etc.
"""

from typing import Generator
from app_db.database import SessionLocal
from sqlalchemy.orm import Session


def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()         # open a new SQLAlchemy session
    try:
        yield db                # provide it to the endpoint
    finally:
        db.close()              # always close