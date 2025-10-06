from datetime import date

from flask import Blueprint, render_template
from sqlalchemy import select

from .models import db, Post

guest_bp = Blueprint("guest", __name__)


@guest_bp.route("/")
@guest_bp.route("/home")
def home():
    today = date.today()
    posts = db.session.scalars(select(Post).where(Post.pub_date <= today))
    return render_template("home.html", posts=posts)


@guest_bp.route("/article/<int:post_id>")
def article(post_id):
    today = date.today()
    post = db.session.execute(select(Post).where(Post.id == post_id, Post.pub_date <= today)).scalar_one_or_none()
    if post is None:
        return "Article not found", 404
    return render_template("article.html", post=post)
