from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse
from typing import List
from uuid import uuid4
from datetime import datetime
from models import Todo, TodoCreate, TodoUpdate

router = APIRouter()

### Setting up in-memory DB
todos = [
    {
        "id": str(uuid4()),
        "title": "Learn FastAPI",
        "description": "Read official FastAPI documentation.",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": str(uuid4()),
        "title": "Build Todo API",
        "description": "Create RESTful API for managing tasks using FastAPI.",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": str(uuid4()),
        "title": "Implement error handling",
        "description": "Implement proper error handling and status codes.",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": str(uuid4()),
        "title": "Add Validation",
        "description": "Create Pydantic models with validation.",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": str(uuid4()),
        "title": "Write unit tests",
        "description": "Write unit tests using pytest (minimum 80% coverage).",
        "completed": False,
        "created_at": datetime.now(),
    },
]

### Implementing Helper Functions
#### Find task by ID:

def get_todo_by_id(todo_id: str):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return None

#### Empty/whitespace only title:

def is_blank(s: str | None) -> bool:
    return s is None or s.strip() == ''

### Implementing API Endpoints
#### Creating a new task

"""
Decorator Explanation:
1. @router.post("/todos/"): 
- FastAPI route decorator - it registers this function as a handler for HTTP POST method and URL path /todos/
- When a POST request to /todos/, FastAPI will call this function: create_todo(todo: TodoCreate)
2. response_model=Todo: Whatever this function returns, serialize it into JSON using the Todo model schema. FastAPI will:
- Validate that the returned object matches the Todo structure.
- Automatically convert datatypes (like datetime) to JSON-friendly formats.
- Exclude any extra fields not defined in the model.
"""

@router.post("/todos/", response_model = Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, response: Response):
    
    if is_blank(todo.title):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty.")
    if any(t['title'].strip().lower() == todo.title.strip().lower() for t in todos):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task with this title already exists.")
    
    new_todo = Todo(
        id = str(uuid4()),
        title = todo.title,
        description = todo.description,
        completed = todo.completed,
        created_at = datetime.now()
    )
    todos.append(new_todo.model_dump())
    response.headers["Location"] = f"/todos/{new_todo.id}"
    return new_todo

#### Retrieving all tasks
@router.get("/todos/", response_model=List[Todo], status_code=status.HTTP_200_OK)
def get_all_todos():
    return todos

#### Retrieving one task by ID:
@router.get("/todos/{todo_id}", response_model=Todo, status_code=status.HTTP_200_OK)
def get_todo(todo_id: str):
    todo = get_todo_by_id(todo_id)
    if not todo:        #if there is no task by that id
        raise HTTPException(status_code=404, detail="Task not found")
    return todo

#### Updating task:
##### Updating specific part of task - PATCH
@router.patch("/todos/{todo_id}", response_model=Todo, status_code=status.HTTP_200_OK) #update by ID
def update_todo(todo_id: str, todo_data: TodoUpdate):
    todo = get_todo_by_id(todo_id)
    if not todo:        #if there is no task by that id
        raise HTTPException(status_code=404, detail="Task not found")
    if todo_data.title is not None:
        todo["title"] = todo_data.title
    if todo_data.description is not None:
        todo["description"] = todo_data.description
    if todo_data.completed is not None:
        todo["completed"] = todo_data.completed
    return Todo(**todo)

""" For this function, user would have to enter all fields, even ones that do not require an update. 
The above would allow requests like: {"completed": true} """

##### Updating entire task:
@router.put("/todos/{todo_id}", response_model=Todo, status_code=status.HTTP_200_OK)
def replace_todo(todo_id: str, todo_data: TodoCreate):
    todo = get_todo_by_id(todo_id)
    if not todo:        #if there is no task by that id
        raise HTTPException(status_code=404, detail="Task not found")
    todo['title'] = todo_data.title
    todo['description'] = todo_data.description
    todo['completed'] = todo_data.completed
    return Todo(**todo)

#### Deleting a task:
@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: str):
    todo = get_todo_by_id(todo_id)
    if not todo:        #if there is no task by that id
        raise HTTPException(status_code=404, detail="Task not found")
    todos.remove(todo)
    return

### Adding Input Validation and Error Handling
#### Input Validation with Pydantic
"""
FastAPI automatically validates input data against the Pydantic models we defined. This ensures that the data meets our expected schema before it’s processed.
"""