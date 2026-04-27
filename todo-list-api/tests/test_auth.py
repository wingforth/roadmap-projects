import json


def register(client, name="Alice", email="alice@example.com", password="secret"):
    return client.post(
        "/register",
        data=json.dumps({"name": name, "email": email, "password": password}),
        content_type="application/json",
    )


def login(client, email="alice@example.com", password="secret"):
    return client.post(
        "/login",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )


def test_register_login_refresh_logout(client):
    # register
    rv = register(client)
    assert rv.status_code == 201
    body = rv.get_json()
    assert "access_token" in body and "refresh_token" in body

    # login
    rv = login(client)
    assert rv.status_code == 200
    body = rv.get_json()
    access = body["access_token"]
    refresh = body["refresh_token"]

    # access protected endpoint should work
    rv = client.post(
        "/todos",
        headers={"Authorization": f"Bearer {access}"},
        data=json.dumps({"title": "t", "description": "d"}),
        content_type="application/json",
    )
    assert rv.status_code == 201

    # refresh token rotate
    rv = client.post(
        "/refresh",
        data=json.dumps({"refresh_token": refresh}),
        content_type="application/json",
    )
    assert rv.status_code == 200
    new_tokens = rv.get_json()
    assert "access_token" in new_tokens and "refresh_token" in new_tokens
    assert refresh != new_tokens["refresh_token"]
    assert access != new_tokens["access_token"]

    # logout using the rotated refresh token (should revoke it)
    rv = client.post(
        "/logout",
        data=json.dumps({"refresh_token": new_tokens["refresh_token"]}),
        content_type="application/json",
    )
    assert rv.status_code == 204

    # trying to refresh with the same token should fail
    rv = client.post(
        "/refresh",
        data=json.dumps({"refresh_token": new_tokens["refresh_token"]}),
        content_type="application/json",
    )
    assert rv.status_code == 401
