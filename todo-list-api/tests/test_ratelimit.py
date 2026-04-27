import json


def register(client, name="Carol", email="carol@example.com", password="pwd123"):
    return client.post(
        "/register",
        data=json.dumps({"name": name, "email": email, "password": password}),
        content_type="application/json",
    )


def login(client, email="carol@example.com", password="pwd123"):
    return client.post(
        "/login",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )


def test_auth_rate_limit(client_auth_ratelimit):
    """Set RATELIMIT_AUTH_LIMITS to "3/minute" in config.json
    in instance folder before this test.
    """

    # register the user first
    rv = register(client_auth_ratelimit)
    assert rv.status_code == 201

    # two successful logins (limit is 3/min as set in tests/conftest.py env)
    rv = login(client_auth_ratelimit)
    assert rv.status_code == 200
    rv = login(client_auth_ratelimit)
    assert rv.status_code == 200

    # the next login should be rate-limited
    rv = login(client_auth_ratelimit)
    assert rv.status_code == 429
    body = rv.get_json()
    assert body.get("error") == "Too Many Requests"
    assert body.get("code") == 429


def register_and_get_tokens(client, name="Bob", email="bob@example.com", password="pwd456"):
    rv = client.post(
        "/register",
        data=json.dumps({"name": name, "email": email, "password": password}),
        content_type="application/json",
    )
    data = rv.get_json()
    return data["access_token"], data["refresh_token"]


def test_crud_todo_flow(client_crud_ratelimit):
    """Set RATELIMIT_CRUD_LIMITS to "3/minute" in config.json
    in instance folder before this test.
    """

    access, _ = register_and_get_tokens(client_crud_ratelimit)

    # create
    rv = client_crud_ratelimit.post(
        "/todos",
        headers={"Authorization": f"Bearer {access}"},
        data=json.dumps({"title": "Buy milk", "description": "2 liters"}),
        content_type="application/json",
    )
    assert rv.status_code == 201

    tid = rv.get_json()["id"]

    # update
    rv = client_crud_ratelimit.put(
        f"/todos/{tid}",
        headers={"Authorization": f"Bearer {access}"},
        data=json.dumps({"title": "Buy milk and eggs"}),
        content_type="application/json",
    )
    assert rv.status_code == 200

    # list
    rv = client_crud_ratelimit.get("/todos", headers={"Authorization": f"Bearer {access}"})
    assert rv.status_code == 200

    # delete
    rv = client_crud_ratelimit.delete(f"/todos/{tid}", headers={"Authorization": f"Bearer {access}"})
    assert rv.status_code == 429
