import json
from datetime import datetime, UTC

from app import app as flask_app


def register_and_get_tokens(client):
    rv = client.post(
        "/register",
        data=json.dumps({"name": "Bob", "email": "bob@example.com", "password": "pwd"}),
        content_type="application/json",
    )
    data = rv.get_json()
    return data["access_token"], data["refresh_token"]


def test_crud_todo_flow(client):
    access, _ = register_and_get_tokens(client)

    # create
    rv = client.post(
        "/todos",
        headers={"Authorization": f"Bearer {access}"},
        data=json.dumps({"title": "Buy milk", "description": "2 liters"}),
        content_type="application/json",
    )
    assert rv.status_code == 201
    todo = rv.get_json()
    tid = todo["id"]

    # update
    rv = client.put(
        f"/todos/{tid}",
        headers={"Authorization": f"Bearer {access}"},
        data=json.dumps({"title": "Buy milk and eggs"}),
        content_type="application/json",
    )
    assert rv.status_code == 200

    # list (default pagination)
    rv = client.get("/todos", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert rv.status_code == 200
    assert data["data"] and data["data"][0]["title"].startswith("Buy milk")
    assert data["page"] == 1 and data["limit"] == flask_app.config["TODO_PAGE_SIZE_DEFAULT"] and data["total"] == 1

    # delete
    rv = client.delete(f"/todos/{tid}", headers={"Authorization": f"Bearer {access}"})
    assert rv.status_code == 204

    # pagination (create additional tasks)
    for i in range(1, 8):
        client.post(
            "/todos",
            headers={"Authorization": f"Bearer {access}"},
            data=json.dumps({"title": "Buy milk", "description": f"{i} liters"}),
            content_type="application/json",
        )
    rv = client.get("/todos?page=2&limit=3", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert data["data"] and len(data["data"]) == 3 and data["data"][0]["description"] == "4 liters"
    assert data["page"] == 2 and data["limit"] == 3 and data["total"] == 3

    # search and sort
    rv = client.get("/todos?search=milk&sort=createdAt", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert len(data["data"]) == 7 and data["data"][0]["description"] == "1 liters"

    # search and sort
    rv = client.get("/todos?search=milk&sort=createdAt&order=desc", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert data["data"] and data["data"][0]["description"] == "7 liters"

    # date range filter- should include created tasks for today
    today = datetime.now(tz=UTC).date().isoformat()
    rv = client.get(f"/todos?date={today}", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert data["total"] == 7
