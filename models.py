"""
## WITHOUT DB CONNECTION
### Defining todo schema

from pydantic import BaseModel, StrictBool
from typing import Optional
from datetime import datetime

class Todo(BaseModel):
    id: str     #unique id for each todo
    title: str  #main content of todo
    description: Optional[str] = None   #additional details, optional
    completed: StrictBool        #status of todo (complete/incomplete)
    created_at: datetime   #timestamp of when todo was created

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: StrictBool = False

### PATCH (update) endpoint
class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[StrictBool] = None
"""

from pydantic import BaseModel, StrictBool, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class TaskRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    created_at: datetime
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime
    created_by: UUID
    assignee_ids: List[UUID] = Field(default_factory=list)
    tag_ids: List[UUID] = Field(default_factory=list)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "normal"
    due_at: Optional[datetime] = None
    created_by: UUID
    assignee_ids: List[UUID] = Field(default_factory=list)
    tag_ids: List[UUID] = Field(default_factory=list)

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_at: Optional[datetime] = None
    assignee_ids: Optional[List[UUID]] = None  # None=no change; []=clear all
    tag_ids: Optional[List[UUID]] = None       # None=no change; []=clear all