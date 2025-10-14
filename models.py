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
