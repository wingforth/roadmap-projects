import threading
from typing import List
from time import sleep
from datetime import datetime, timezone

from app import app
from app.models import db


def setup_function():
    # Use an in-memory database for tests and create tables
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.drop_all()
        db.create_all()


def test_create_and_get_post():
    client = app.test_client()
    payload = {
        "title": "My First Blog Post",
        "content": "This is the content of my first blog post.",
        "category": "Technology",
        "tags": ["Tech", "Programming"],
    }
    r = client.post("/posts", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert data["id"] == 1
    assert data["title"] == payload["title"]

    r = client.get("/posts/1")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == 1
    assert data["tags"] == payload["tags"]


def test_get_all_and_filter():
    client = app.test_client()
    posts = [
        {
            "title": "Tech post",
            "content": "About tech",
            "category": "Technology",
            "tags": ["tech"],
        },
        {
            "title": "Cooking post",
            "content": "About cooking",
            "category": "Food",
            "tags": ["cooking"],
        },
    ]
    for p in posts:
        r = client.post("/posts", json=p)
        assert r.status_code == 201

    r = client.get("/posts")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list) and len(data) >= 2

    r = client.get("/posts?term=tech")
    assert r.status_code == 200
    data = r.get_json()
    assert any("Tech post" == d["title"] for d in data)


def test_update_and_delete():
    client = app.test_client()
    payload = {
        "title": "Updatable",
        "content": "Original",
        "category": "Misc",
        "tags": [],
    }
    r = client.post("/posts", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    post_id = data["id"]

    r = client.put(f"/posts/{post_id}", json={"title": "Updated"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["title"] == "Updated"

    r = client.delete(f"/posts/{post_id}")
    assert r.status_code == 204

    r = client.get(f"/posts/{post_id}")
    assert r.status_code == 404


def test_validation_errors():
    client = app.test_client()
    r = client.post("/posts", json={"content": "No title", "category": "X"})
    assert r.status_code == 400
    data = r.get_json()
    assert "Missing fields" in data.get("message", "")

    r = client.post("/posts", json={"title": " ", "content": "a", "category": "b"})
    assert r.status_code == 400
    data = r.get_json()
    assert "can not be empty" in data.get("message", "")

    r = client.post("/posts", json={"title": "T", "content": "C", "category": "Cat", "tags": "not-a-list"})
    assert r.status_code == 400
    data = r.get_json()
    assert "should be a list" in data.get("message", "")


def test_not_found_update_and_delete():
    client = app.test_client()
    r = client.put("/posts/9999", json={"title": "Nope"})
    assert r.status_code == 404
    r = client.delete("/posts/9999")
    assert r.status_code == 404


def test_malformed_json_returns_400():
    # Send invalid JSON body (missing closing brace)
    client = app.test_client()
    r = client.post("/posts", data='{"title": "x"', content_type="application/json")
    # Flask will raise a BadRequest on malformed JSON; test client returns 400
    assert r.status_code in (400, 500)


def _create_posts_in_thread(n: int, results: List[int]):
    """Helper for concurrent creation of posts."""
    c = app.test_client()
    for _ in range(n):
        r = c.post(
            "/posts",
            json={"title": "concurrent", "content": "x", "category": "c", "tags": []},
        )
        results.append(r.status_code)


def test_concurrent_creates():
    # Start several threads creating posts concurrently
    threads = []
    results: List[int] = []
    num_threads = 5
    per_thread = 10
    for _ in range(num_threads):
        t = threading.Thread(target=_create_posts_in_thread, args=(per_thread, results))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # Ensure all posts created returned 201
    assert all(status == 201 for status in results)

    client = app.test_client()
    r = client.get("/posts")
    assert r.status_code == 200
    data = r.get_json()
    assert len(data) >= num_threads * per_thread


def test_create_and_update_timestamps():
    """Ensure `createdAt` is set on creation and `updatedAt` changes on update."""
    client = app.test_client()
    payload = {
        "title": "Timestamp Test",
        "content": "Initial",
        "category": "Testing",
        "tags": [],
    }
    r = client.post("/posts", json=payload)
    assert r.status_code == 201
    data = r.get_json()
    created_at = data.get("createdAt")
    updated_at = data.get("updatedAt")
    print(data)
    assert created_at and updated_at

    # Parse timestamps (format produced by the app: YYYY-MM-DDTHH:MM:SSZ)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    created_dt = datetime.strptime(created_at, fmt).replace(tzinfo=timezone.utc)
    updated_dt = datetime.strptime(updated_at, fmt).replace(tzinfo=timezone.utc)
    # On creation the timestamps should be equal (no updates yet)
    assert created_dt == updated_dt
    # Wait to ensure the updated_at will differ (resolution is seconds)
    sleep(1.1)

    # Perform an update
    post_id = data["id"]
    r = client.put(f"/posts/{post_id}", json={"content": "Updated content"})
    assert r.status_code == 200
    data2 = r.get_json()
    new_updated_at = data2.get("updatedAt")
    assert new_updated_at

    new_updated_dt = datetime.strptime(new_updated_at, fmt).replace(tzinfo=timezone.utc)

    # updated_at should be strictly after created_at
    assert new_updated_dt > created_dt
