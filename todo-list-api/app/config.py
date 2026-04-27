"""Application configuration defaults.

Environment variables:
- `SECRET_KEY` (optional): Flask secret key.
- `JWT_SECRET_KEY` (required by the app): secret used to sign JWTs.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class DefaultConfig:
    # Prefer an explicit SECRET_KEY, fall back to JWT secret for simple setups
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # JWT secret key
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_EXPIRE_SECOND = 360 * 2
    JWT_REFRESH_EXPIRE_SECOND = 360 * 24 * 7
    # Rate limiting defaults (used by flask-limiter). Can be overridden
    # via instance config.
    RATELIMIT_DEFAULT = "50/day, 20/hour, 10/minute"
    RATELIMIT_AUTH_LIMITS = "50/day, 20/hour"
    RATELIMIT_CRUD_LIMITS = "500/day, 200/hour, 50/minute"
    RATELIMIT_STORAGE_URI = "memory://"
    # Default page size of todo list
    TODO_PAGE_SIZE_DEFAULT = 20


JWT_ALGORITHM = "HS256"
SORT_BY = ("createdAt", "updatedAt")
SORT_ORDER = ("asc", "desc")
