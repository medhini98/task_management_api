from sqlalchemy import (
    Column, String, Text, Enum, ForeignKey, UniqueConstraint, Index, text, 
    TIMESTAMP
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from app_db.database import Base
from enum import Enum as PyEnum

class TaskStatus(str, PyEnum):
    todo = "todo"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"
    cancelled = "cancelled"

class TaskPriority(str, PyEnum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"

class Department(Base):
    __tablename__ = "departments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    roles = relationship("Role", back_populates="department")
    users = relationship("User", back_populates="department")

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    __table_args__ = (UniqueConstraint("department_id", "name", name="uq_role_per_dept"),)
    department = relationship("Department", back_populates="roles")
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    reports_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    department = relationship("Department", back_populates="users")
    role = relationship("Role", back_populates="users")
    manager = relationship("User", remote_side=[id], backref="direct_reports")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, name="task_status"), default=TaskStatus.todo, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority, name="task_priority"), default=TaskPriority.normal, nullable=False)
    created_at = mapped_column(TIMESTAMP(timezone=True), server_default="now()", nullable=False)
    due_at = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    completed_at = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    #updated_at = mapped_column(TIMESTAMP(timezone=True), server_default="now()", nullable=False)
    updated_at = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        server_onupdate=text("now()"),
        nullable=False
    )        # auto-updates on row changes
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    assignees = relationship("User", secondary="task_assignees", backref="tasks")
    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")

class TaskAssignee(Base):
    __tablename__ = "task_assignees"
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = mapped_column(TIMESTAMP(timezone=True), server_default="now()", nullable=False)

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    tasks = relationship("Task", secondary="task_tags", back_populates="tags")

class TaskTag(Base):
    __tablename__ = "task_tags"
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)