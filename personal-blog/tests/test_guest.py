from datetime import date

import pytest
from app.models import db, Post, User
import app.guest as guest


def test_home_route_returns_rendered_template(app, monkeypatch):
    # create a user and a post (avoid FK integrity error)
    user = User(username="guest1", password_hash="x")
    db.session.add(user)
    db.session.commit()

    p = Post(title="t1", content="c1", pub_date=date.today(), author=user)
    db.session.add(p)
    db.session.commit()

    # patch the guest module's render_template to avoid requiring template files
    monkeypatch.setattr("app.guest.render_template", lambda *a, **k: "HOME_OK")

    with app.app_context():
        res = guest.home()
    assert res == "HOME_OK"


def test_article_route_found_and_not_found(app, monkeypatch):
    # patch the guest module's render_template
    monkeypatch.setattr("app.guest.render_template", lambda *a, **k: "ARTICLE_OK")

    # ensure no post -> 404 behavior
    with app.app_context():
        res, status = guest.article(999)
        assert status == 404

    # create a user and a post and test found path
    user = User(username="guest2", password_hash="x")
    db.session.add(user)
    db.session.commit()

    p = Post(title="t2", content="c2", pub_date=date.today(), author=user)
    db.session.add(p)
    db.session.commit()
    with app.app_context():
        res = guest.article(p.id)
    assert res == "ARTICLE_OK"