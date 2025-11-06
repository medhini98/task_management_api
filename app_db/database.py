from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

# Import settings
from core.config import settings
#from app_db.models import Base

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=False)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/task_api")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# --- Auto-create tables if using SQLite (for AWS Lambda demo) ---
#if settings.auto_create_tables and settings.database_url.startswith("sqlite"):
 #   Base.metadata.create_all(bind=engine)

 # --- Auto-create tables if using SQLite (for ECS/Lambda demo) ---
AUTO_CREATE = os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true"
if AUTO_CREATE and DATABASE_URL.startswith("sqlite"):
    # Import models ONLY here so Base knows all tables before create_all
    from app_db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)