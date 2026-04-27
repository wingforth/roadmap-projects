"""Flask view functions for the todo-list API.

Endpoints accept and return JSON. JWT is used for simple auth and the
module validates that a `JWT_SECRET_KEY` is available in the app
configuration on import to fail fast in misconfigured environments.
"""

import time
import uuid
from functools import wraps

import jwt
from flask import jsonify, request, g
from sqlalchemy import select, or_
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.errors import RateLimitExceeded
from pydantic import ValidationError

from app import app
from app.models import db, User, Task, RefreshToken
from app.schemas import UserRegisterSchema, UserLoginSchema, TaskCreateSchema, TaskUpdateSchema, QueryParametersSchema
from app.utils import format_validation_error

JWT_ALGORITHM = "HS256"

db.init_app(app)

# Fail fast if JWT_SECRET_KEY is missing
if not app.config.get("JWT_SECRET_KEY"):
    raise RuntimeError("JWT_SECRET_KEY must be set in app config")


def get_user_id_or_ip():
    return getattr(g, "user_id", None) or request.remote_addr or "127.0.0.1"


limiter = Limiter(key_func=get_user_id_or_ip, app=app)
auth_limit = limiter.shared_limit(app.config["RATELIMIT_AUTH_LIMITS"], scope="auth")
crud_limit = limiter.shared_limit(app.config["RATELIMIT_CRUD_LIMITS"], scope="crud")


def _create_refresh_token(user_id: int) -> str:
    """Create a refresh token JWT and persist its `jti` in the database.

    Returns a tuple `(jti, token_str)` where `jti` is the identifier stored
    in the DB and `token_str` is the encoded JWT returned to the client.
    """
    jti = str(uuid.uuid4())
    exp = int(time.time() + app.config["JWT_REFRESH_EXPIRE_SECOND"])
    token_str = jwt.encode(
        {"user": user_id, "type": "refresh", "jti": jti, "exp": exp},
        app.config["JWT_SECRET_KEY"],
        algorithm=JWT_ALGORITHM,
    )
    rt = RefreshToken(jti=jti, user_id=user_id, expires_at=exp)
    db.session.add(rt)
    db.session.commit()
    return token_str


def _create_access_token(user_id: int) -> str:
    return jwt.encode(
        {
            "user": user_id,
            "type": "access",
            "jti": str(uuid.uuid4()),
            "exp": int(time.time()) + app.config["JWT_ACCESS_EXPIRE_SECOND"],
        },
        app.config["JWT_SECRET_KEY"],
        algorithm=JWT_ALGORITHM,
    )


def generate_token_pair(user_id: int) -> tuple[str, str]:
    access = _create_access_token(user_id)
    refresh = _create_refresh_token(user_id)
    return access, refresh


@app.route("/register", methods=["POST"])
@auth_limit
def register():
    """Register a new user and return an access/refresh token pair.

    Expects JSON with `name`, `email`, `password`.
    """
    register_data = request.get_json(silent=True) or {}
    try:
        register_user = UserRegisterSchema(**register_data)
    except ValidationError as e:
        return jsonify({"message": format_validation_error(e)}), 400

    if db.session.scalar(select(User).where(User.email == register_user.email)):
        return jsonify({"message": "The email has already been registered."}), 409

    new_user = User(
        name=register_user.name, email=register_user.email, password_hash=generate_password_hash(register_user.password)
    )
    db.session.add(new_user)
    db.session.commit()
    access, refresh = generate_token_pair(new_user.id)
    return jsonify({"access_token": access, "refresh_token": refresh}), 201


@app.route("/login", methods=["POST"])
@auth_limit
def login():
    """Authenticate a user and return an access/refresh token pair.

    Expects JSON with `email` and `password`.
    """
    login_data = request.get_json(silent=True) or {}
    try:
        login_user = UserLoginSchema(**login_data)
    except ValidationError as e:
        return jsonify({"message": format_validation_error(e)}), 401

    user = db.session.scalar(select(User).where(User.email == login_user.email))
    if not user:
        return jsonify({"message": "User does not exist."}), 401
    if not check_password_hash(user.password_hash, login_user.password):
        return jsonify({"message": "Password is wrong."}), 401
    access, refresh = generate_token_pair(user.id)
    return jsonify({"access_token": access, "refresh_token": refresh}), 200


def jwt_required(error, code):
    def decorator(view):
        """Decorator factory that enforces a valid access JWT.

        Parameters:
        - error: error string returned in JSON under `error` when failing
        - code: HTTP status code to return on failure
        """

        @wraps(view)
        def wrapper(*args, **kwargs):
            token = None
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return jsonify({"error": error, "message": "Token is missing."}), code
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": error, "message": "Token type error."}), code
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return jsonify({"error": error, "message": "Token has expired"}), code
            except jwt.InvalidTokenError:
                return jsonify({"error": error, "message": "Token is invalid"}), code
            if payload.get("type") != "access":
                return jsonify({"error": error, "message": "Token is not an access token."}), code
            g.user_id = payload.get("user")
            if not g.user_id:
                return jsonify({"error": error, "message": "Token missing user ID."}), code
            return view(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/todos", methods=["POST"])
@jwt_required("Unauthorized", 401)
@crud_limit
def create_todo():
    data = request.get_json(silent=True) or {}
    try:
        todo = TaskCreateSchema(**data)
    except ValidationError as e:
        return jsonify({"message": format_validation_error(e)}), 400

    task = Task(title=todo.title, description=todo.description, user_id=g.user_id)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@app.route("/todos/<int:task_id>", methods=["PUT"])
@jwt_required("Forbidden", 403)
@crud_limit
def update_todo(task_id):
    task = db.session.scalar(select(Task).where(Task.id == task_id, Task.user_id == g.user_id))
    if not task:
        return jsonify({"message": f"Task ({task_id}) does not exist."}), 404

    data = request.get_json(silent=True) or {}
    try:
        updated_fields = TaskUpdateSchema(**data).model_dump(exclude_unset=True)
    except ValidationError as e:
        return jsonify({"message": format_validation_error(e)}), 400

    if title := updated_fields.get("title"):
        task.title = title
    if description := updated_fields.get("description"):
        task.description = description
    if status := updated_fields.get("status"):
        task.status = status
    db.session.commit()
    return jsonify(task.to_dict()), 200


@app.route("/todos/<int:task_id>", methods=["DELETE"])
@jwt_required("Forbidden", 403)
@crud_limit
def delete_todo(task_id):
    task = db.session.scalar(select(Task).where(Task.id == task_id, Task.user_id == g.user_id))
    if not task:
        return jsonify({"message": f"Task ({task_id}) does not exist."}), 404
    db.session.delete(task)
    db.session.commit()
    return "", 204


@app.route("/todos", methods=["GET"])
@jwt_required("Forbidden", 403)
@crud_limit
def get_todos():
    args = request.args.to_dict()
    args.setdefault("limit", app.config.get("TODO_PAGE_SIZE_DEFAULT", 20))
    try:
        query_params = QueryParametersSchema.model_validate(args, by_alias=True).model_dump(exclude_none=True)
    except ValidationError as e:
        return jsonify({"message": format_validation_error(e)}), 400

    # collect where clauses
    where_clauses = [Task.user_id == g.user_id]
    # filter by date
    if date_range := query_params.get("dates"):
        where_clauses.extend([Task.created_at >= date_range[0], Task.created_at < date_range[1]])
    # text search against `title` and `description`
    if search := query_params.get("search"):
        like_pattern = f"%{search}%"
        where_clauses.append(or_(Task.title.ilike(like_pattern), Task.description.ilike(like_pattern)))
    stmt = select(Task).where(*where_clauses)

    # sort todo list by `created_at`, `updated_at` or `status`
    if sort_by := query_params.get("sort_by"):
        sort_clause = getattr(Task, sort_by)
        if sort_order := query_params.get("sort_order"):
            sort_clause = getattr(sort_clause, sort_order)()
        stmt = stmt.order_by(sort_clause)

    page_number, page_size = query_params["page_num"], query_params["page_size"]
    offset = (page_number - 1) * page_size
    stmt = stmt.limit(page_size).offset(offset)
    todos = db.session.scalars(stmt).all()
    return jsonify(
        {
            "data": [t.to_dict() for t in todos],
            "page": page_number,
            "limit": page_size,
            "total": len(todos),
            "dates": date_range or (),
        }
    ), 200


@app.route("/refresh", methods=["POST"])
@auth_limit
def refresh_token():
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return jsonify({"message": "Missing refresh token."}), 400
    try:
        payload = jwt.decode(refresh_token, key=app.config["JWT_SECRET_KEY"], algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "The refresh token has expired, please log in again."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "The refresh token is invalid"}), 401
    if payload.get("type") != "refresh":
        return jsonify({"message": "Token is not a refresh token."}), 401
    jti = payload.get("jti")
    if not jti:
        return jsonify({"message": "Refresh token missing identifier."}), 401

    # rotate: revoke the used refresh token and issue a new one
    token_row = db.session.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if not token_row:
        return jsonify({"message": "The refresh token has been deleted, please log in again."}), 401
    if token_row.revoked:
        return jsonify({"message": "The refresh token has been revoked, please log in again."}), 401
    token_row.revoked = True
    db.session.commit()
    access = _create_access_token(payload["user"])
    new_refresh = _create_refresh_token(payload["user"])
    return jsonify({"access_token": access, "refresh_token": new_refresh}), 200


@app.route("/logout", methods=["POST"])
def logout():
    """Revoke a refresh token provided by the client (log out).

    The client should POST `{ "refresh_token": "..." }`.
    """
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return jsonify({"message": "Missing refresh token."}), 400
    try:
        payload = jwt.decode(refresh_token, key=app.config["JWT_SECRET_KEY"], algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid refresh token."}), 401
    if payload.get("type") != "refresh":
        return jsonify({"message": "Token is not a refresh token."}), 401
    jti = payload.get("jti")
    if not jti:
        return jsonify({"message": "Refresh token missing identifier."}), 400
    token = db.session.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if token:
        token.revoked = True
        db.session.commit()
    return "", 204


@app.errorhandler(RateLimitExceeded)
def rate_limit_exceed(error):
    return (
        jsonify(
            {
                "error": "Too Many Requests",
                "code": 429,
                "message": f"Rate limit exceeded: {error.description}",
                "path": request.path,
                "retry_after": error.retry_after,
            }
        ),
        429,
    )
