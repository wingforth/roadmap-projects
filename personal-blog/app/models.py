"""SQLAlchemy models for the personal-blog example.

This module defines the ORM models and a small helper that enables
SQLite foreign-key enforcement for pysqlite connections.
"""

from __future__ import annotations
from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy import ForeignKey, Engine, event
from sqlite3 import Connection as SqliteConnection


class Base(DeclarativeBase):
    """Base class for SQLAlchemy mapped classes."""

    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    """User account.

    Attributes:
        id: integer primary key
        username: unique username
        password_hash: hashed password string
        posts: relationship to Post objects authored by this user
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    posts: Mapped[list["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan", passive_deletes=True
    )


class Post(db.Model):
    """Blog post.

    Attributes:
        id: integer primary key
        title: post title
        content: post content (text)
        pub_date: publication date
        author_id: foreign key to users.id (ondelete cascade)
        author: relationship to the User that authored the post
    """

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str]
    pub_date: Mapped[date] = mapped_column(default=date.today)
    author_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"), nullable=False)

    author: Mapped["User"] = relationship(back_populates="posts")


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Enable PRAGMA foreign_keys=ON for sqlite3 connections.

    This listener runs on each Engine.connect. It only acts when the
    DB-API connection is an instance of sqlite3.Connection (pysqlite).
    """
    if not isinstance(dbapi_connection, SqliteConnection):
        return
    # the sqlite3 driver will not set PRAGMA foreign_keys
    # if autocommit=False; set to True temporarily
    ac = dbapi_connection.autocommit
    dbapi_connection.autocommit = True

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    # restore previous autocommit setting
    dbapi_connection.autocommit = ac
