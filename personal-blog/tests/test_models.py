import pytest
from sqlalchemy import func, select

from app.models import db, User, Post


def test_create_user_and_post(app):
    """User and Post can be created and relationship/author access works."""
    u = User(username="alice", password_hash="x")
    db.session.add(u)
    db.session.commit()

    p = Post(title="Hello", content="content", author=u)
    db.session.add(p)
    db.session.commit()

    assert p.author is not None
    assert p.author.username == "alice"


def test_delete_user_cascades_posts(app):
    """Deleting a User removes associated Posts (ORM + DB cascade)."""
    u = User(username="bob", password_hash="x")
    db.session.add(u)
    db.session.commit()

    p = Post(title="T", content="c", author=u)
    db.session.add(p)
    db.session.commit()

    # delete user
    db.session.delete(u)
    db.session.commit()

    remaining = db.session.scalar(select(func.count()).select_from(Post))
    assert remaining == 0
