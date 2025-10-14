"""
Covers: create, list, get, patch (partial), put (full), delete (204), 404, 400, 422.
"""

from fastapi import status

def create_sample(client, title="Write tests with pytest", desc="pytest 80%", completed=False):
    res = client.post(
        "/todos/",
        json={"title": title, "description": desc, "completed": completed},
    )
    assert res.status_code == status.HTTP_201_CREATED  #make sure status code is the one for "created"
    data = res.json()
    assert {"id", "title", "description", "completed", "created_at"} <= set(data.keys())  #make sure all required fields are present
    return data

def test_create_and_list(client):
    create_sample(client)
    res = client.get("/todos/")
    assert res.status_code == status.HTTP_200_OK #make sure status code is correct
    data = res.json()
    assert isinstance(data, list)  #Confirms the shape of the response from GET /todos/ is a list
    assert len(data) == 1  #reset_state fixture clears the in-memory store before each test, and this test creates exactly one todo via _create_sample, the list should have exactly one item.
    assert data[0]["title"] == "Write tests with pytest"

def test_get_single(client):
    created = create_sample(client)
    res = client.get(f"/todos/{created['id']}")
    assert res.status_code == status.HTTP_200_OK  #make sure status code is correct
    assert res.json()["id"] == created["id"]  #make sure retrieved ID matches entered ID

def test_patch_partial_update(client):
    created = create_sample(client, completed=False)
    res = client.patch(f"/todos/{created['id']}", json={"completed": True})
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["completed"] is True   ##makes sure replacement is done correctly

def test_put_full_replace(client):
    created = create_sample(client)
    res = client.put(
        f"/todos/{created['id']}",
        json={"title": "Replaced", "description": "All new", "completed": True},
    )
    assert res.status_code == status.HTTP_200_OK  #make sure status code is correct
    body = res.json()
    assert body["title"] == "Replaced"  #makes sure replacements are done correctly
    assert body["description"] == "All new"
    assert body["completed"] is True

def test_delete_204(client):
    created = create_sample(client)
    res = client.delete(f"/todos/{created['id']}")
    assert res.status_code == status.HTTP_204_NO_CONTENT  #Confirms the delete endpoint returns the proper status and no body (204)
    #subsequent get should 404
    res2 = client.get(f"/todos/{created['id']}")
    assert res2.status_code == status.HTTP_404_NOT_FOUND  #After deletion, trying to fetch the same ID should return 404 Not Found because it no longer exists
    err = res2.json()
    #HTTPException handler returns {"error": "...", "path": ..., ...}
    assert "error" in err #Verifies the error response schema defined in HTTPException handler - checks error body shape is as per API

def test_get_404_nonexistent(client):
    res = client.get("/todos/does-not-exist")
    assert res.status_code == status.HTTP_404_NOT_FOUND
    body = res.json()
    assert body["error"] == "Task not found"  #makes sure error message matches API - from HTTPException(detail="Task not found")

def test_post_400_blank_title(client):
    res = client.post(
        "/todos/",
        json={"title": "   ", "description": "x", "completed": False},
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    body = res.json()
    assert "error" in body
    assert body["error"] == "Title cannot be empty."

def test_post_409_duplicate_title(client):
    """Ensure creating a todo with a duplicate title returns 409 Conflict."""

    # Step 1: Create a todo with a specific title
    first = client.post("/todos/", json={"title": "Learn FastAPI", "description": "Intro to FastAPI", "completed": False})
    assert first.status_code == status.HTTP_201_CREATED

    # Step 2: Try creating another todo with the same title (case-insensitive)
    dup = client.post("/todos/", json={"title": "learn fastapi", "description": "Duplicate test", "completed": False})
    assert dup.status_code == status.HTTP_409_CONFLICT

    # Step 3: Check the response body
    body = dup.json()
    assert "error" in body or "detail" in body  # depending on handler shape
    assert "already exists" in (body.get("error") or body.get("detail"))


def test_post_422_wrong_types(client):
    # completed must be bool; send string to trigger RequestValidationError
    res = client.post(
        "/todos/",
        json={"title": "Bad types", "description": "x", "completed": "yes"},
    )
    assert res.status_code == 422
    body = res.json()
    # custom validation handler returns {"error": "Validation failed", ...}
    assert body.get("error") == "Validation failed"
    assert "details" in body  #make sure it returns structured list of validation issues (exc.errors())

