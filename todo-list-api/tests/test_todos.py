import json
from datetime import date


def register_and_get_tokens(client):
    rv = client.post(
        "/register",
        data=json.dumps({"name": "Bob", "email": "bob@example.com", "password": "pwd123"}),
        content_type="application/json",
    )
    data = rv.get_json()
    return data["access_token"], data["refresh_token"]


def test_crud_todo_flow(client, app):
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
    assert data["page"] == 1 and data["limit"] == app.config["TODO_PAGE_SIZE_DEFAULT"] and data["total"] == 1

    # delete
    rv = client.delete(f"/todos/{tid}", headers={"Authorization": f"Bearer {access}"})
    assert rv.status_code == 204

    # pagination (create additional tasks)
    for i in range(1, 5):
        client.post(
            "/todos",
            headers={"Authorization": f"Bearer {access}"},
            data=json.dumps({"title": f"Buy milk {i}", "description": f"{i} liters milk"}),
            content_type="application/json",
        )
    for i in range(5, 10):
        client.post(
            "/todos",
            headers={"Authorization": f"Bearer {access}"},
            data=json.dumps({"title": f"Buy oil {i}", "description": f"{i} liters oil"}),
            content_type="application/json",
        )
    rv = client.get("/todos?page=2&limit=3", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert data["data"] and len(data["data"]) == 3 and data["data"][0]["description"] == "4 liters milk"
    assert data["page"] == 2 and data["limit"] == 3 and data["total"] == 3

    # search
    rv = client.get("/todos?search=oil", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert data["data"] and len(data["data"]) == 5

    # sort
    rv = client.get("/todos?sortBy=createdAt&sortOrder=desc", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert data["data"] and data["data"][0]["description"] == "9 liters oil"

    # date range filter should include created tasks for today
    today = date.today().isoformat()
    rv = client.get(f"/todos?dates={today}", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert data["total"] == 9
    today = "2026-05-10,2026-05-13"
    rv = client.get(f"/todos?dates={today}", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert data["total"] == 0

    rv = client.get("/todos?sortBy=created&sortOrder=down&dates=2311", headers={"Authorization": f"Bearer {access}"})
    data = rv.get_json()
    assert rv.status_code == 400
    assert "message" in data
    err_msg = data["message"]
    assert "dates" in err_msg and "sortBy" in err_msg and "sortOrder" in err_msg
