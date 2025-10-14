"""
- Creates a FastAPI TestClient
- Resets in-memory DB (todos) before every test so tests don’t leak state
"""

import pytest
from fastapi.testclient import TestClient

"""
Reset State - Decorator:
- @pytest.fixture: 
    - Decorator provided by pytest.
    - Tells pytest that the following function is a fixture — a reusable setup function that can prepare resources for tests (like initializing data, creating clients, etc.).
- autouse=True: 
    - Run this fixture automatically before every test without having to explicitly include it in the test function. 
    - So reset_state() will run before every test, even if it is not mentioned in the test function parameters.

Function:
This fixture’s job is to reset or clear your app’s in-memory database (the todos list) before each test, so that tests don’t interfere with one another.
"""
@pytest.fixture(autouse=True)
def reset_state():
    # Clear in-memory store before each test
    from routers import todo as todo_module   #imports the todo module from routers package
    todo_module.todos.clear()        #accesses the global list todos defined in routers/todo.py, .clear() empties the list in-place

"""
client - Decorator:
- @pytest.fixture: defines another fixture (without autouse=True this time)
- explicitly ask for it in test functions (by adding client as a function argument)
Function:
- Its job is to create a FastAPI test client — a lightweight object that can simulate HTTP requests (GET, POST, PATCH, etc.) to app without running a real server
- with TestClient(app) as c:
    - TestClient is a helper from FastAPI (internally using requests) that allows you to send HTTP requests directly to your app in tests.
    - Using with ensures proper setup and teardown — for example, if your app had startup/shutdown events or background tasks, they’ll be handled cleanly.
    - It creates a temporary testing client object named c.
- yield c: yields the client to tests
"""

@pytest.fixture
def client():
    from main import app  # imports FastAPI app
    with TestClient(app) as c:  
        yield c