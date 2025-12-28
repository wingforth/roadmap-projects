"""Database models for the blogging platform.

This module declares a single SQLAlchemy ``db`` instance and the ``Post``
model used by the API. The module provides a small helper ``init_app`` to
create database tables when the Flask application is initialized.
"""

from datetime import datetime, timezone
from json import loads, dumps
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Return the current UTC time as an aware ``datetime``.

    Using an aware datetime ensures consistent storage and easy conversion to
    an RFC3339-like string with a trailing ``Z`` in responses.
    """
    return datetime.now(tz=timezone.utc)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models used by Flask-SQLAlchemy."""


db = SQLAlchemy(model_class=Base)


class Post(db.Model):
    """A blog post stored in the database.

    Attributes:
        id: Auto-incrementing primary key.
        title: Post title.
        content: Post body content.
        category: Category name.
        tags: JSON-encoded list of tags (stored as a text column).
        created_at: UTC creation timestamp.
        updated_at: UTC last update timestamp.
    """

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    tags: Mapped[str] = mapped_column(nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow, onupdate=utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a JSON-serializable dictionary.

        The timestamps are formatted as UTC RFC3339-like strings ending with
        ``Z`` (for example ``2021-09-01T12:00:00Z``).
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": loads(self.tags),
            "createdAt": self.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updatedAt": self.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def update(
        self,
        *,
        title: str | None = None,
        content: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Update fields on the model in-place.

        Only fields that are not ``None`` are applied.
        """
        if title is not None:
            self.title = title
        if content is not None:
            self.content = content
        if category is not None:
            self.category = category
        if tags is not None:
            self.tags = dumps(tags)
