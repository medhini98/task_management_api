"""
DB-backed integration tests for the Task API.

Covers:
- list (GET /todos/)
- create → get → delete roundtrip
- 404 on missing task
- patch to mark complete (sets status=done, completed_at != null)
- 400 on invalid enum value
"""

from uuid import UUID, uuid4
from datetime import datetime
from fastapi import status


def _pick_ids(client):
    """Fetch one valid user & tag from the API (seed.py must have run)."""
    users = client.get("/users").json()
    tags = client.get("/tags").json()
    assert users, "No users found; run `python seed.py` first."
    assert tags, "No tags found; run `python seed.py` first."
    user_id = users[0]["id"]
    tag_id = tags[0]["id"]
    return user_id, tag_id


def test_list_returns_array(client):
    res = client.get("/todos/")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert isinstance(data, list)


def test_create_get_delete_task_flow(client):
    created_by, tag_id = _pick_ids(client)
    assignee_id = created_by  # keep it simple

    payload = {
        "title": "E2E: fast test",
        "description": "roundtrip CRUD",
        "status": "todo",
        "priority": "normal",
        "created_by": created_by,
        "assignee_ids": [assignee_id],
        "tag_ids": [tag_id],
    }

    # Create
    r = client.post("/todos/", json=payload)
    assert r.status_code == status.HTTP_201_CREATED, r.text
    task = r.json()
    task_id = task["id"]
    UUID(task_id)

    # Get
    r = client.get(f"/todos/{task_id}")
    assert r.status_code == status.HTTP_200_OK
    got = r.json()
    assert got["title"] == payload["title"]
    assert got["assignee_ids"] == [assignee_id]
    assert got["tag_ids"] == [tag_id]

    # Delete
    r = client.delete(f"/todos/{task_id}")
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # Confirm 404
    r = client.get(f"/todos/{task_id}")
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_patch_mark_complete_sets_done_and_timestamp(client):
    created_by, tag_id = _pick_ids(client)

    # Create a todo first
    r = client.post(
        "/todos/",
        json={
            "title": "complete me",
            "description": "mark done",
            "created_by": created_by,
            "assignee_ids": [created_by],
            "tag_ids": [tag_id],
        },
    )
    assert r.status_code == status.HTTP_201_CREATED, r.text
    task_id = r.json()["id"]

    # Patch: completed=true
    r = client.patch(f"/todos/{task_id}", json={"completed": True})
    assert r.status_code == status.HTTP_200_OK
    body = r.json()
    assert body["status"] == "done"
    assert body["completed_at"] is not None
    # quick ISO8601 parse check
    datetime.fromisoformat(body["completed_at"].replace("Z", "+00:00"))

    # cleanup
    client.delete(f"/todos/{task_id}")


def test_get_404_for_random_uuid(client):
    random_id = uuid4()
    r = client.get(f"/todos/{random_id}")
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_post_400_invalid_status_enum(client):
    created_by, tag_id = _pick_ids(client)
    r = client.post(
        "/todos/",
        json={
            "title": "bad status",
            "description": "should 400",
            "status": "not_a_real_status",
            "priority": "normal",
            "created_by": created_by,
            "assignee_ids": [created_by],
            "tag_ids": [tag_id],
        },
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST

"""
 Exercises branches for filters and error paths that router already supports.
 These small tests hit:
	•	the filters paths (status, assignee_id, tag_id),
	•	both 400 branches (invalid assignee/tag),
	•	patch invalid priority (another 400),
	•	clearing M2M via empty lists.
"""

def _ids(client):
    users = client.get("/users").json()
    tags = client.get("/tags").json()
    assert users and tags, "Run `python seed.py` first"
    return users[0]["id"], tags[0]["id"]

def test_list_filter_by_status(client):
    creator, tag_id = _ids(client)

    # create a todo with status=in_progress
    r = client.post("/todos/", json={
        "title": "filter-by-status",
        "status": "in_progress",
        "priority": "normal",
        "created_by": creator,
        "assignee_ids": [creator],
        "tag_ids": [tag_id],
    })
    assert r.status_code == status.HTTP_201_CREATED
    tid = r.json()["id"]

    # filter
    r = client.get("/todos/?status=in_progress")
    assert r.status_code == 200
    assert any(t["id"] == tid for t in r.json())

    # cleanup
    client.delete(f"/todos/{tid}")

def test_list_filter_by_assignee_and_tag(client):
    creator, tag_id = _ids(client)

    r = client.post("/todos/", json={
        "title": "filter-by-assignee-tag",
        "status": "todo",
        "priority": "high",
        "created_by": creator,
        "assignee_ids": [creator],
        "tag_ids": [tag_id],
    })
    assert r.status_code == 201
    tid = r.json()["id"]

    r = client.get(f"/todos/?assignee_id={creator}&tag_id={tag_id}")
    assert r.status_code == 200
    ids = [t["id"] for t in r.json()]
    assert tid in ids

    client.delete(f"/todos/{tid}")

def test_post_400_invalid_assignee_id(client):
    creator, tag_id = _ids(client)
    bad_user_id = uuid4()  # not in DB

    r = client.post("/todos/", json={
        "title": "bad-assignee",
        "status": "todo",
        "priority": "normal",
        "created_by": creator,
        "assignee_ids": [str(bad_user_id)],
        "tag_ids": [tag_id],
    })
    assert r.status_code == status.HTTP_400_BAD_REQUEST

def test_post_400_invalid_tag_id(client):
    creator, _ = _ids(client)
    bad_tag_id = uuid4()

    r = client.post("/todos/", json={
        "title": "bad-tag",
        "status": "todo",
        "priority": "normal",
        "created_by": creator,
        "assignee_ids": [creator],
        "tag_ids": [str(bad_tag_id)],
    })
    assert r.status_code == status.HTTP_400_BAD_REQUEST

def test_patch_400_invalid_priority(client):
    creator, tag = _ids(client)
    # create
    r = client.post("/todos/", json={
        "title": "bad-priority",
        "created_by": creator,
        "assignee_ids": [creator],
        "tag_ids": [tag],
    })
    assert r.status_code == 201
    tid = r.json()["id"]

    # patch invalid priority
    r = client.patch(f"/todos/{tid}", json={"priority": "not_a_real_priority"})
    assert r.status_code == status.HTTP_400_BAD_REQUEST

    client.delete(f"/todos/{tid}")

def test_patch_clear_assignees_and_tags(client):
    creator, tag = _ids(client)
    # create with both
    r = client.post("/todos/", json={
        "title": "clear-m2m",
        "created_by": creator,
        "assignee_ids": [creator],
        "tag_ids": [tag],
    })
    assert r.status_code == 201
    tid = r.json()["id"]

    # clear both by sending empty arrays
    r = client.patch(f"/todos/{tid}", json={"assignee_ids": [], "tag_ids": []})
    assert r.status_code == 200
    body = r.json()
    assert body["assignee_ids"] == []
    assert body["tag_ids"] == []

    client.delete(f"/todos/{tid}")