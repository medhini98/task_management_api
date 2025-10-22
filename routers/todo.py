# routers/todo.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app_db.session import get_session
from app_db import models as dbm
from models import TaskRead, TaskCreate, TaskUpdate

router = APIRouter()

def to_task_read(t: dbm.Task) -> TaskRead:
    # Map ORM Task -> Pydantic TaskRead
    return TaskRead(
        id=t.id,
        title=t.title,
        description=t.description,
        status=t.status.value,
        priority=t.priority.value,
        created_at=t.created_at,
        due_at=t.due_at,
        completed_at=t.completed_at,
        updated_at=t.updated_at,
        created_by=t.created_by,
        assignee_ids=[u.id for u in t.assignees],
        tag_ids=[tag.id for tag in t.tags],
    )

#@router.get("/todos/", response_model=List[TaskRead])
#def list_tasks(db: Session = Depends(get_session)):
#    tasks = db.query(dbm.Task).order_by(dbm.Task.created_at.desc()).all()
#    return [to_task_read(t) for t in tasks]

@router.get("/todos/", response_model=List[TaskRead])
def list_tasks(
    status: Optional[str] = Query(None),
    assignee_id: Optional[UUID] = Query(None),
    tag_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_session),
):
    q = db.query(dbm.Task)
    if status:
        try:
            q = q.filter(dbm.Task.status == dbm.TaskStatus(status))
        except ValueError:
            raise HTTPException(400, "Invalid status")
    if assignee_id:
        q = q.join(dbm.Task.assignees).filter(dbm.User.id == assignee_id)
    if tag_id:
        q = q.join(dbm.Task.tags).filter(dbm.Tag.id == tag_id)

    tasks = q.order_by(dbm.Task.created_at.desc()).all()
    return [to_task_read(t) for t in tasks]

@router.get("/todos/{task_id}", response_model=TaskRead)
def get_task(task_id: UUID, db: Session = Depends(get_session)):
    t = db.get(dbm.Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return to_task_read(t)

@router.post("/todos/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_session)):
    # Validate/convert enums
    try:
        status_enum = dbm.TaskStatus(payload.status) if payload.status else dbm.TaskStatus.todo
        priority_enum = dbm.TaskPriority(payload.priority) if payload.priority else dbm.TaskPriority.normal
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status or priority")

    t = dbm.Task(
        title=payload.title,
        description=payload.description,
        status=status_enum,
        priority=priority_enum,
        due_at=payload.due_at,
        created_by=payload.created_by,
    )

    # Assignees
    if payload.assignee_ids:
        users = db.query(dbm.User).filter(dbm.User.id.in_(payload.assignee_ids)).all()
        if len(users) != len(set(payload.assignee_ids)):
            raise HTTPException(status_code=400, detail="One or more assignee_ids are invalid")
        t.assignees = users

    # Tags
    if payload.tag_ids:
        tags = db.query(dbm.Tag).filter(dbm.Tag.id.in_(payload.tag_ids)).all()
        if len(tags) != len(set(payload.tag_ids)):
            raise HTTPException(status_code=400, detail="One or more tag_ids are invalid")
        t.tags = tags

    db.add(t)
    db.commit()
    db.refresh(t)
    return to_task_read(t)

@router.patch("/todos/{task_id}", response_model=TaskRead)
@router.patch("/todos/{task_id}", response_model=TaskRead)
def patch_task(task_id: UUID, payload: TaskUpdate, db: Session = Depends(get_session)):
    t = db.get(dbm.Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    # simple fields
    if payload.title is not None:
        t.title = payload.title
    if payload.description is not None:
        t.description = payload.description
    if payload.due_at is not None:
        t.due_at = payload.due_at

    # status: validate enum + maintain completed_at
    if payload.status is not None:
        new_status = payload.status
        # Optional synonym:
        # if new_status == "completed":
        #     new_status = "done"

        try:
            t.status = dbm.TaskStatus(new_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

        if t.status == dbm.TaskStatus.done:
            if t.completed_at is None:
                t.completed_at = datetime.now(timezone.utc)
        else:
            # moving out of done -> clear timestamp
            t.completed_at = None

    # priority: validate enum
    if payload.priority is not None:
        try:
            t.priority = dbm.TaskPriority(payload.priority)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid priority")

    # Replace assignees if provided (None = no change, [] = clear)
    if payload.assignee_ids is not None:
        users = (
            db.query(dbm.User)
              .filter(dbm.User.id.in_(payload.assignee_ids))
              .all()
            if payload.assignee_ids else []
        )
        if payload.assignee_ids and len(users) != len(set(payload.assignee_ids)):
            raise HTTPException(status_code=400, detail="One or more assignee_ids are invalid")
        t.assignees = users

    # Replace tags if provided (None = no change, [] = clear)
    if payload.tag_ids is not None:
        tags = (
            db.query(dbm.Tag)
              .filter(dbm.Tag.id.in_(payload.tag_ids))
              .all()
            if payload.tag_ids else []
        )
        if payload.tag_ids and len(tags) != len(set(payload.tag_ids)):
            raise HTTPException(status_code=400, detail="One or more tag_ids are invalid")
        t.tags = tags

    db.commit()
    db.refresh(t)
    return to_task_read(t)

@router.delete("/todos/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, db: Session = Depends(get_session)):
    t = db.get(dbm.Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(t)
    db.commit()
    return