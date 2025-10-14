# Task Management API

A simple yet complete **FastAPI-based Task Management API** that supports full **CRUD operations**, **input validation**, **custom error handling**, and **automated tests with 96% coverage**.  
This project demonstrates clean architecture and best practices in API design using **FastAPI**, **Pydantic**, and **Pytest**.

---

## Features

- Modular structure with routers (`routers/todo.py`)  
- CRUD operations for `/todos`  
- Request & response validation using **Pydantic models**  
- Custom error handlers for:
    - `HTTPException`
    - `RequestValidationError`

- Proper HTTP status codes (200, 201, 204, 400, 404, 409, 422)  
- Interactive API docs via **Swagger UI** & **ReDoc**  
- Automated tests with **Pytest** — 96% coverage  

---

## Tech Stack

| Layer | Technology |
|:------|:------------|
| Framework | FastAPI |
| Data Models | Pydantic |
| Testing | Pytest + HTTPX |
| Language | Python 3.13 |
| Docs | OpenAPI / Swagger UI |
| Coverage | `pytest-cov` |

---

## Project Structure
fastapi-todo-app/
│
|-- main.py                 # App entry point
|-- models.py               # Pydantic models (Todo, TodoCreate, TodoUpdate)
|-- routers/
│   |-- init.py
│   |-- todo.py             # CRUD route handlers
│
|-- tests/
│   |-- conftest.py         # Fixtures for testing
│   |-- test_todos.py       # Test suite (CRUD + validation + errors)
│
|-- requirements.txt
|-- .gitignore

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

## API Endpoints

| Method | Endpoint | Description |
|:-------|:----------|:-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/current-time` | Get server time |
| `GET` | `/todos/` | Retrieve all tasks |
| `GET` | `/todos/{id}` | Retrieve a specific task |
| `POST` | `/todos/` | Create a new task |
| `PATCH` | `/todos/{id}` | Partially update a task |
| `PUT` | `/todos/{id}` | Replace an existing task |
| `DELETE` | `/todos/{id}` | Delete a task |

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
Run the test suite with coverage:
```bash
    PYTHONPATH=. pytest --cov=./ --cov-report=term-missing -q
```

Ran twice - Failure on first run:

**Pytest Result**:
| File Path              | Stmts | Miss | Cover | Missing Lines              |
|-------------------------|:-----:|:----:|:------:|-----------------------------|
| `main.py`              | 22    | 4    | 82%   | 10, 14–15, 58              |
| `models.py`            | 17    | 0    | 100%  | —                          |
| `routers/__init__.py`  | 0     | 0    | 100%  | —                          |
| `routers/todo.py`      | 65    | 5    | 92%   | 115, 117, 119, 132, 143    |
| `tests/conftest.py`    | 13    | 0    | 100%  | —                          |
| `tests/test_todos.py`  | 66    | 3    | 95%   | 101–104                    |
| **TOTAL**              | **183** | **12** | **93%** | —                          |

---

**Test Summary**:
| Result | Description |
|:--------|:-------------|
| ✅ 8 Passed | All CRUD and validation tests passed successfully |
| ⚠️ 1 Failed | `test_post_422_wrong_types` – expected 422, got 201 (fixed in final version) |
| ⚙️ 7 Warnings | Pydantic deprecation warnings for `.dict()` (expected in v2) |
| ⏱ Duration | ~0.15 seconds |

---

- Overall Coverage: 93%  

---

- Correction Made:
Update all models in models.py:
From: completed: Bool To: completed: StrictBool

---

**Coverage after correction (2nd run)**:

| File Path              | Stmts | Miss | Cover | Missing Lines              |
|-------------------------|:-----:|:----:|:------:|-----------------------------|
| `main.py`              | 22    | 3    | 86%   | 10, 14–15                  |
| `models.py`            | 17    | 0    | 100%  | —                          |
| `routers/__init__.py`  | 0     | 0    | 100%  | —                          |
| `routers/todo.py`      | 65    | 5    | 92%   | 115, 117, 119, 132, 143    |
| `tests/conftest.py`    | 13    | 0    | 100%  | —                          |
| `tests/test_todos.py`  | 66    | 0    | 100%  | —                          |
| **TOTAL**              | **183** | **8** | **96%** | —                          |

**Test Summary**:
| Result | Description |
|:--------|:-------------|
| ✅ 9 Passed | All CRUD, validation, and error-handling tests successful |
| ⚙️ 0 Failed | No failed tests in this run |
| 🧩 Warnings | Pydantic `.dict()` deprecation (expected for v2) |
| ⏱ Duration | ~0.10 seconds |

---

> **Overall Coverage:** 96%  
> **Status:** All functionality validated and tested successfully.

##### See detailed browser test results and screenshots in [API_Testing_Demo.md](API_Testing_Demo.md)

## Resources

- [CRUD – GeeksforGeeks](https://www.geeksforgeeks.org/websites-apps/crud-full-form/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Routing in Python – Tutorialspoint](https://www.tutorialspoint.com/python_network_programming/python_routing.htm)
- [Routing in Python – Python Wiki](https://wiki.python.org/moin/Routing)
- [FastAPI – APIRouter Reference](https://fastapi.tiangolo.com/reference/apirouter/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)
- [Test Coverage using Pytest – Medium](https://martinxpn.medium.com/test-coverage-in-python-with-pytest-86-100-days-of-python-a3205c77296)
- [FastAPI Todo App Guide (Parts 1–6) – James B Mour](https://dev.to/jamesbmour/fastapi-part-1-introduction-to-fastapi-3l73)