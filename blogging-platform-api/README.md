# Blogging Platform API

A small RESTful JSON API for a personal blogging platform. It provides basic CRUD operations (Create, Read, Update, Delete) for blog posts and a simple text search endpoint.

## Features

- Create, read, update, and delete blog posts
- Search posts by term across title, category and tags
- SQLite default database (configurable)

## Requirements

- Python 3.14+
-  Python package and project manager: [uv](https://docs.astral.sh/uv/)

## Quick start

1. Create python virtual environment, and install dependencies:

```bash
uv sync
```

2. Run the development server:

```bash
uv run run.py
```

By default the server runs on `http://127.0.0.1:5000`.

## Configuration

Default configuration values are in `app/config.py`.

- `SQLALCHEMY_DATABASE_URI` defaults to `sqlite:///blog.db` (a `blog.db` file is created in the working directory).
- `SECRET_KEY` has a development default; override it in production.

To override settings create an instance config file at `instance/config.py` (this file is loaded automatically if present) or set environment variables used by Flask.

Example `instance/config.py`:

```python
SECRET_KEY = "your-secret-key"
SQLALCHEMY_DATABASE_URI = "sqlite:///instance_blog.db"
```

## API Overview

Base URL: `http://127.0.0.1:5000`

All endpoints return JSON and use standard HTTP status codes.

### Post object schema

Request fields (JSON):

- `title` (string, required for create)
- `content` (string, required for create)
- `category` (string, required for create)
- `tags` (array of strings, optional)

Response fields (JSON):

- `id` (integer)
- `title`, `content`, `category`
- `tags` (array of strings)
- `createdAt`, `updatedAt` (RFC3339-like UTC strings ending with `Z`)

### Endpoints

- Create a post

  - Method: `POST /posts`
  - Body: JSON with `title`, `content`, `category`, optional `tags` (array)
  - Success: `201 Created` + created post JSON
  - Example:

```bash
curl -sS -X POST http://127.0.0.1:5000/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","content":"World","category":"personal","tags":["intro","first"]}'
```

- Get all posts (optionally search)

  - Method: `GET /posts`
  - Query param: `term` (optional) — case-insensitive substring search across title, category and tags
  - Success: `200 OK` + array of posts
  - Example:

```bash
curl -sS "http://127.0.0.1:5000/posts?term=intro"
```

- Get a single post by id

  - Method: `GET /posts/{id}`
  - Success: `200 OK` + post JSON; Not found: `404`
  - Example:

```bash
curl -sS http://127.0.0.1:5000/posts/1
```

- Update a post (partial updates supported)

  - Method: `PUT /posts/{id}`
  - Body: JSON with any of `title`, `content`, `category`, `tags`
  - Success: `200 OK` + updated post JSON; Not found: `404`; Validation error: `400`
  - Example (change title):

```bash
curl -sS -X PUT http://127.0.0.1:5000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated title"}'
```

- Delete a post

  - Method: `DELETE /posts/{id}`
  - Success: `204 No Content`; Not found: `404`
  - Example:

```bash
curl -sS -X DELETE http://127.0.0.1:5000/posts/1
```

### Examples using Python `requests`

Install `requests` in your environment and use the snippets below.

Create a post:

```python
import requests

base = "http://127.0.0.1:5000"
payload = {
    "title": "My post",
    "content": "Hello world",
    "category": "notes",
    "tags": ["personal", "notes"]
}
resp = requests.post(f"{base}/posts", json=payload)
resp.raise_for_status()
print(resp.json())
```

Search posts:

```python
resp = requests.get(f"{base}/posts", params={"term": "notes"})
resp.raise_for_status()
print(resp.json())
```

Update a post:

```python
resp = requests.put(f"{base}/posts/1", json={"title": "New Title"})
resp.raise_for_status()
print(resp.json())
```

Delete a post:

```python
resp = requests.delete(f"{base}/posts/1")
if resp.status_code == 204:
    print("Deleted")
else:
    print(resp.status_code, resp.text)
```

## Implementation notes

- The API uses Flask and Flask-SQLAlchemy. Database models are in `app/models.py` and routes are implemented in `app/views.py`.
- The `tags` column is stored as JSON-encoded text in the database and returned as an array in responses.

## Next steps / Suggestions

- Add request authentication (JWT or API keys) for multi-user or production usage.
- Add pagination and sorting to `GET /posts` for large datasets.
- Add input sanitization and rate limiting for public deployments.
