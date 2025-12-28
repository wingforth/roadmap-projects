import pytest
from sqlalchemy import select, func
from click.testing import CliRunner

from app.cli import add_user, list_user, list_post, change_password, delete_user
from app.models import db, User, Post
from werkzeug.security import generate_password_hash, check_password_hash


def test_add_user_command(app):
    """add-user CLI creates a user when invoked with --password."""
    runner = CliRunner()
    with app.app_context():
        result = runner.invoke(add_user, ["charlie", "--password", "pw"])
        assert result.exit_code == 0
        u = db.session.execute(select(User).where(User.username == "charlie")).one_or_none()
        assert u is not None


def test_list_user_command(app):
    """list-user prints usernames."""
    runner = CliRunner()
    with app.app_context():
        db.session.add(User(username="diana", password_hash="x"))
        db.session.commit()
        result = runner.invoke(list_user)
        assert result.exit_code == 0
        assert "diana" in result.output


def test_list_post_command(app):
    """list-post prints posts; --user filters by username."""
    runner = CliRunner()
    with app.app_context():
        u1 = User(username="u1", password_hash="x")
        u2 = User(username="u2", password_hash="x")
        db.session.add_all([u1, u2])
        db.session.commit()

        p1 = Post(title="p1", content="c1", author=u1)
        p2 = Post(title="p2", content="c2", author=u2)
        db.session.add_all([p1, p2])
        db.session.commit()

        res = runner.invoke(list_post)
        assert res.exit_code == 0
        assert "p1" in res.output and "p2" in res.output

        res = runner.invoke(list_post, ["--user", "u1"])
        assert res.exit_code == 0
        assert "p1" in res.output and "p2" not in res.output


def test_change_password_command(app):
    """change-password updates stored password hash."""
    runner = CliRunner()
    with app.app_context():
        db.session.add(User(username="changeme", password_hash=generate_password_hash("old")))
        db.session.commit()

        res = runner.invoke(change_password, ["changeme", "--password", "newpw"])
        assert res.exit_code == 0

        updated = db.session.execute(select(User).where(User.username == "changeme")).scalar_one()
        assert check_password_hash(updated.password_hash, "newpw")


def test_delete_user_command(app):
    """delete-user removes user and associated posts when confirmed."""
    runner = CliRunner()
    with app.app_context():
        u = User(username="delme", password_hash="x")
        db.session.add(u)
        db.session.commit()

        p = Post(title="pdel", content="c", author=u)
        db.session.add(p)
        db.session.commit()

        # confirm deletion by sending 'y' input
        res = runner.invoke(delete_user, ["delme"], input="y\n")
        assert res.exit_code == 0

        exists = db.session.execute(select(User).where(User.username == "delme")).one_or_none()
        assert exists is None

        remaining = db.session.scalar(select(func.count()).select_from(Post))
        assert remaining == 0
