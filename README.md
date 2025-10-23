# Task Management API (Database-Backed)

A production-ready FastAPI Task Management API built with PostgreSQL, SQLAlchemy ORM, and Alembic migrations.
This project extends the in-memory FastAPI version into a full persistent, relational database-driven API, complete with validation, custom error handling, and Pytest-based integration tests.

⸻

## Features

- Modular and scalable architecture with clear separation between:
- routers/ – FastAPI route handlers
- app_db/ – Database, ORM models, and session handling
- tests/ – Integration tests and fixtures
- Full CRUD operations for /todos with persistent storage
- Database-backed relationships:
- Users ↔ Tasks (many-to-many via task_assignees)
- Tasks ↔ Tags (many-to-many via task_tags)
- Auto-managed timestamps (created_at, updated_at, completed_at)
- Enum-based task status and priority
- Custom validation and error responses (HTTPException, RequestValidationError)
- Alembic-based schema migrations
- Integrated Pytest test suite with >90% coverage


---


## Tech Stack

| **Layer**     | **Technology**                 |
|----------------|--------------------------------|
| Framework      | FastAPI                        |
| ORM            | SQLAlchemy                     |
| Database       | PostgreSQL                     |
| Migrations     | Alembic                        |
| Validation     | Pydantic                       |
| Testing        | Pytest + pytest-cov            |
| Language       | Python 3.13                    |
| Docs           | Swagger UI / ReDoc (OpenAPI)   |

---

## Project Structure
fastapi-todo-app/
│
├── main.py                  # FastAPI entrypoint
├── models.py                # Pydantic schemas (TaskRead, TaskCreate, etc.)
│
├── app_db/
│   ├── __init__.py
│   ├── database.py          # SQLAlchemy engine + Base setup
│   ├── models.py            # SQLAlchemy ORM models & relationships
│   ├── session.py           # DB session dependency
│
├── routers/
│   ├── __init__.py
│   ├── todo.py              # CRUD endpoints for /todos
│   ├── lookup.py            # Endpoints for /users and /tags
│
├── tests/
│   ├── conftest.py          # Test DB fixture & client setup
│   ├── test_todos.py        # Integration tests for DB-backed API
│
├── alembic/                 # Auto-generated migration scripts
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── requirements.txt
├── .env                     # Contains DATABASE_URL
└── README.md

---

## ⚙️ Installation & Setup

### 1. Clone the repo
```bash
    git clone https://github.com/medhini98/task_management_api.git
    cd task_management_api
```

### 2. Create & activate a virtual environment
```bash
    python -m venv .venv
    source .venv/bin/activate
```
### 3. Install dependencies
```bash
    pip install -r requirements.txt
```

### 4. Configure Environment
Create a .env file in the root:
```bash
DATABASE_URL=postgresql+psycopg://postgres:<your_password>@localhost:5432/task_api
```

### 5. Initialize the Database

Run migrations:
```bash
alembic upgrade head
```
If the database doesn’t exist yet:
```bash
createdb -U postgres task_api
```

## API Endpoints

| **Method** | **Endpoint**      | **Description**                                         |
|-------------|------------------|---------------------------------------------------------|
| GET         | `/`              | Welcome message                                         |
| GET         | `/current-time`  | Get current server time                                 |
| GET         | `/todos/`        | Retrieve all tasks (filter by status/assignee/tag)      |
| GET         | `/todos/{id}`    | Retrieve a specific task                                |
| POST        | `/todos/`        | Create a new task                                       |
| PATCH       | `/todos/{id}`    | Partially update task (status, tags, assignees, etc.)   |
| DELETE      | `/todos/{id}`    | Delete a task                                           |
| GET         | `/users/`        | Retrieve all users                                      |
| GET         | `/tags/`         | Retrieve all tags                                       |

## Schema Overview

Tables
- Users: basic user info, department & role relations
- Tasks: title, description, status, priority, timestamps, foreign keys
- Tags: categorical labels for tasks
- TaskAssignees: join table (Users ↔ Tasks)
- TaskTags: join table (Tasks ↔ Tags)

**Example Task (JSON)**:
```json
{
  "id": "140fb6c2-a36e-4641-915c-b7a90387c8da",
  "title": "Build auth module",
  "description": "Implement JWT-based auth with refresh tokens.",
  "status": "in_progress",
  "priority": "high",
  "created_at": "2025-10-22T16:03:20.057497+05:30",
  "due_at": "2025-10-29T11:57:18.465135+05:30",
  "completed_at": null,
  "updated_at": "2025-10-22T17:27:18.465829+05:30",
  "created_by": "71ede514-166e-48aa-8788-e2c6f9fc78d3",
  "assignee_ids": ["71ede514-166e-48aa-8788-e2c6f9fc78d3"],
  "tag_ids": ["92adc1de-b266-473c-a23f-6064f6ec6578"]
}
```

## Error Handling

| Status | Case | Response |
|:-------|:------|:----------------|
| **400** | Blank title | `{ "error": "Title cannot be empty." }` |
| **404** | Todo not found | `{ "error": "Task not found" }` |
| **409** | Duplicate title | `{ "error": "Task with this title already exists." }` |
| **422** | Validation error | `{ "error": "Validation failed" }` |

## Running the API
```bash
    uvicorn main:app --reload
```
Then open your browser at: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs

## Running Tests using Pytest
Run all tests with coverage:
```bash
    pytest --cov=./ --cov-report=term-missing --cov-fail-under=80 -v
```

**Test Summary**:

| **Metric**       | **Result**        |
|-------------------|------------------|
| Total tests       | 11               |
| Passed            | 11               |
| Failed            | 0                |
| Coverage          | 93.05%           |
| Duration          | ~0.6 seconds     |

---

## Coverage Breakdown

| **File**              | **Coverage** |
|------------------------|--------------|
| main.py                | 83%          |
| routers/todo.py        | 86%          |
| app_db/models.py       | 100%         |
| app_db/session.py      | 100%         |
| tests/test_todos.py    | 100%         |
| **Overall**            | **93%**      |

> **Status:** All CRUD operations, validations, and DB integrations working successfully.

##### See detailed browser test results and screenshots in [API_Testing_Demo.md](API_Testing_Demo.md)

## Key Behavior Validations

| **Case**              | **Expected Outcome**                                      |
|------------------------|-----------------------------------------------------------|
| Create Task            | 201 Created with valid UUID                              |
| Fetch Task             | Returns JSON with matching `id`                          |
| Update Status          | Auto-stamps `completed_at` when `status = done`          |
| Clear Assignees/Tags   | Empty arrays successfully clear M2M relations            |
| Invalid UUID           | 422 Validation error                                     |
| Invalid Enum           | 400 Bad Request                                          |
| Delete Task            | 204 No Content                                           |

## Notes & Design Decisions

- Normalization: schema normalized up to BCNF (all non-key attributes depend on the key)
- Enums: used for status & priority instead of booleans
- Timestamps: timezone-aware (TIMESTAMP WITH TIME ZONE)
- Error Handling: centralized handlers return consistent JSON shape
- Indexes: added for faster dashboard queries (status, due_at, email)
- Alembic Discipline: one migration per schema change

## Resources

- [CRUD – GeeksforGeeks](https://www.geeksforgeeks.org/websites-apps/crud-full-form/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Routing in Python – Tutorialspoint](https://www.tutorialspoint.com/python_network_programming/python_routing.htm)
- [Routing in Python – Python Wiki](https://wiki.python.org/moin/Routing)
- [FastAPI – APIRouter Reference](https://fastapi.tiangolo.com/reference/apirouter/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)
- [Test Coverage using Pytest – Medium](https://martinxpn.medium.com/test-coverage-in-python-with-pytest-86-100-days-of-python-a3205c77296)
- [FastAPI Todo App Guide (Parts 1–6) – James B Mour](https://dev.to/jamesbmour/fastapi-part-1-introduction-to-fastapi-3l73)