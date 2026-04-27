"""Database models for the todo-list API.

This module defines the `User` and `Task` models and configures a small
Engine listener to enable SQLite foreign key support when using the
pysqlite driver.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, UTC

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, String, Integer, ForeignKey, event, Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for SQLAlchemy mapped classes."""


db = SQLAlchemy(model_class=Base)


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


class User(db.Model):
    """A registered user who owns tasks.

    Attributes
    - id: primary key
    - name, email, password_hash: credentials
    - tasks: list of `Task` instances owned by the user
    - refresh_token: list of `RefreshToken` instances owned by the user
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Task(db.Model):
    """A todo task belonging to a `User`.

    The `created_at` and `updated_at` fields use database-side defaults so
    the values are set by the database engine.

    Attributes:
    - id (int): primary key
    - title (str): short task title
    - description (str): detailed description
    - created_at (datetime): timestamp when created
    - updated_at (datetime): timestamp when last updated (DB onupdate)
    - user_id (int): foreign key referencing `users.id`
    """

    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    # Store UTC datetimes and set defaults in the application
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="tasks")

    def to_dict(self) -> dict:
        """Serialize a `Task` instance to a JSON-serializable dict."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            # Return ISO-8601 strings in local time.
            "created_at": self.created_at.replace(tzinfo=UTC).astimezone().isoformat(),
            "updated_at": self.updated_at.replace(tzinfo=UTC).astimezone().isoformat(),
        }


class RefreshToken(db.Model):
    """Stores refresh tokens for users so they can be revoked/rotated.

    Fields:
    - `jti`: unique token identifier stored in the JWT payload
    - `user_id`: owner
    - `revoked`: whether this refresh token has been revoked
    - `expires_at`: when the refresh token expires
    """

    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    revoked: Mapped[bool] = mapped_column(nullable=False, default=False)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Enable `PRAGMA foreign_keys=ON` for sqlite3 connections."""
    if not isinstance(dbapi_connection, sqlite3.Connection):
        return

    # the sqlite3 driver will not set PRAGMA foreign_keys
    # if autocommit=False; set to True temporarily
    ac = dbapi_connection.autocommit
    dbapi_connection.autocommit = True

    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()

    # restore previous autocommit setting
    dbapi_connection.autocommit = ac
