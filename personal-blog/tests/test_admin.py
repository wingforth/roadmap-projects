import pytest

import app.admin as admin


def test_admin_login_route(monkeypatch, app):
    # if implemented, test that login route returns template (monkeypatch)
    monkeypatch.setattr("app.admin.render_template", lambda *a, **k: "LOGIN_OK")
    with app.test_request_context(method="GET", path="/login"):
        res = admin.login()
        assert res == "LOGIN_OK"
