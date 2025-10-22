"""
- Creates a FastAPI TestClient that talks to the live DB (task_api via .env / app_db.database).
- No in-memory reset needed; we are not storing state in a Python list anymore.
"""

import sys, pathlib
import pytest
from fastapi.testclient import TestClient

# --- Ensure we can import from project root (fastapi-todo-app/) ---
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------------------------

"""
client - Decorator:
- @pytest.fixture: defines the test client fixture (request it by adding `client` to your test function).
Function:
- Creates a FastAPI test client — sends HTTP requests directly into the app without a real server.
- Uses your app's production wiring (DB session dependency, models, routers).
"""
@pytest.fixture()
def client():
    from main import app  # import FastAPI app (includes routers)
    with TestClient(app) as c:
        yield c


"""
Optional: sanity pre-check so tests fail with a friendly message
instead of cryptic errors if the DB is empty.

- This fixture is autouse=True so it runs before every test.
- It verifies that at least one user and one tag exist (from seed.py).
- If not present, it raises a helpful assertion telling you to run `python seed.py`.
"""
@pytest.fixture(autouse=True)
def _sanity_seed_check(client):
    users = client.get("/users").json()
    tags = client.get("/tags").json()
    assert users, "No users found. Run `python seed.py` to seed development data."
    assert tags, "No tags found. Run `python seed.py` to seed development data."