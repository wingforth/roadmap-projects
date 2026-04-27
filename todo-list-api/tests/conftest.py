import json
from pathlib import Path

import pytest


@pytest.fixture
def app():
    file = Path(__file__).resolve().parent.parent / "instance/config.json"
    with open(file, mode="r+") as fd:
        config = json.load(fd)
        config["RATELIMIT_AUTH_LIMITS"] = "300/minute"
        config["RATELIMIT_CRUD_LIMITS"] = "300/minute"
        fd.seek(0)
        json.dump(config, fd, indent=4)

    from app import app as flask_app
    from app.models import db

    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        JWT_SECRET_KEY="test-secret",
        SECRET_KEY="test-secret",
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def client_auth_ratelimit():
    file = Path(__file__).resolve().parent.parent / "instance/config.json"
    with open(file, mode="r+") as fd:
        config = json.load(fd)
        config["RATELIMIT_AUTH_LIMITS"] = "3/minute"
        config["RATELIMIT_CRUD_LIMITS"] = "300/minute"
        fd.seek(0)
        json.dump(config, fd, indent=4)

    from app import app as flask_app
    from app.models import db

    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        JWT_SECRET_KEY="test-secret",
        SECRET_KEY="test-secret",
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client_crud_ratelimit():
    file = Path(__file__).resolve().parent.parent / "instance/config.json"
    with open(file, mode="r+") as fd:
        config = json.load(fd)
        config["RATELIMIT_AUTH_LIMITS"] = "300/minute"
        config["RATELIMIT_CRUD_LIMITS"] = "3/minute"
        fd.seek(0)
        json.dump(config, fd, indent=4)

    from app import app as flask_app
    from app.models import db

    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        JWT_SECRET_KEY="test-secret",
        SECRET_KEY="test-secret",
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()
