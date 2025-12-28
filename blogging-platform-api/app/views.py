"""Flask views (HTTP routes) for the blogging platform API.

This module exposes a small RESTful JSON API for creating, reading,
updating and deleting blog posts.
"""

from json import dumps
from typing import Any, Dict, Tuple

from flask import jsonify, request
from sqlalchemy import select, or_

from app import app
from app.models import db, Post


# Initialize the single shared SQLAlchemy `db` instance declared in `app.models`.
db.init_app(app)


_POST_FIELDS = ("title", "content", "category", "tags")
_POST_REQUIRED_FIELDS = ("title", "content", "category")


def validate_data(request_json_data: dict | None, total: bool = True) -> Tuple[bool, Dict[str, Any]]:
    """Validate incoming JSON payload for post create/update.

    Args:
        request_json_data: Parsed JSON payload from the request or ``None``.
        total: When True, require all required fields to be present.

    Returns:
        A tuple ``(is_valid, data_or_errors)``. When valid, ``data_or_errors`` is
        a dict suitable for constructing/updating a ``Post`` instance. When
        invalid, it is a dict with ``error`` and ``message`` keys for the client.
    """
    if not isinstance(request_json_data, dict):
        return False, {"error": "Invalid data", "message": "JSON body is required."}

    if total and (missed_fields := set(_POST_REQUIRED_FIELDS).difference(request_json_data.keys())):
        return False, {"error": "Invalid data", "message": f"Missing fields: {', '.join(sorted(missed_fields))}"}

    if invalid_fields := set(request_json_data.keys()).difference(_POST_FIELDS):
        return False, {"error": "Invalid data", "message": f"Invalid fields: {', '.join(sorted(invalid_fields))}"}

    validated_data: dict[str, Any] = {}
    for field, val in request_json_data.items():
        if field == "tags":
            if not isinstance(val, list):
                return False, {"error": "Invalid data", "message": f"Field '{field}' should be a list."}
            validated_data[field] = dumps(val)
            continue
        if not isinstance(val, str):
            return False, {"error": "Invalid data", "message": f"Field '{field}' should be a string."}
        if not (val := val.strip()):
            return False, {
                "error": "Invalid data",
                "message": f"Field '{field}' can not be empty or a whitespace string.",
            }
        validated_data[field] = val

    return True, validated_data


@app.post("/posts")
def create_post():
    """Create a new blog post.

    Expects a JSON body with ``title``, ``content``, ``category`` and optional
    ``tags`` (list). Returns 201 with the created post or 400 on validation
    errors.
    """
    ok, data = validate_data(request.get_json())
    if not ok:
        return jsonify(data), 400
    post = Post(**data)
    with db.session.begin():
        db.session.add(post)
    return jsonify(post.to_dict()), 201


@app.put("/posts/<int:post_id>")
def update_post(post_id: int):
    """Update an existing blog post by id.

    Accepts a partial body (only provided fields will be updated).
    Returns 200 with the updated post, 400 for validation errors, or 404 if
    the post does not exist.
    """
    with db.session.begin():
        post = db.session.get(Post, post_id)
        if post is None:
            return jsonify({"error": "Not Found", "message": f"The blog post does not exist: {post_id}"}), 404
        ok, data = validate_data(request.get_json(), total=False)
        if not ok:
            return jsonify(data), 400
        post.update(**data)
    return jsonify(post.to_dict()), 200


@app.delete("/posts/<int:post_id>")
def delete_post(post_id: int):
    """Delete a blog post. Returns 204 on success or 404 if not found."""
    with db.session.begin():
        post = db.session.get(Post, post_id)
        if post is None:
            return jsonify({"error": "Not Found", "message": f"The blog post does not exist: {post_id}"}), 404
        db.session.delete(post)
    return "", 204


@app.get("/posts/<int:post_id>")
def get_post_by_id(post_id: int):
    """Return a single blog post by id. 404 if not found."""
    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify({"error": "Not Found", "message": f"The blog post does not exist: {post_id}"}), 404
    return jsonify(post.to_dict()), 200


@app.get("/posts")
def get_all_post():
    """Return all posts. If ``term`` query param is present, perform a
    case-insensitive wildcard search on title, category or tags.
    """
    query = select(Post)
    if term := (request.args.get("term") or "").strip():
        like_pattern = f"%{term}%"
        query = query.filter(
            or_(Post.title.ilike(like_pattern), Post.category.ilike(like_pattern), Post.tags.ilike(like_pattern))
        )
    posts = db.session.scalars(query.order_by(Post.created_at.asc())).all()
    return jsonify([post.to_dict() for post in posts]), 200
