from datetime import date, datetime
from functools import wraps

from flask import Blueprint, url_for, render_template, flash, redirect, request, session
from sqlalchemy import select
from werkzeug.security import check_password_hash

from app.models import db, Post, User

admin_bp = Blueprint("admin", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" in session:
            return view(*args, **kwargs)
        return redirect(url_for("admin.login"))

    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password_hash, password):
            error = "Incorrect password."
        else:
            session["user"] = user.username
            session["user_id"] = user.id
            return redirect(url_for("admin.dashboard"))
        flash(error)
    return render_template("login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("guest.home"))


@admin_bp.route("/admin")
@login_required
def dashboard():
    posts = db.session.scalars(select(Post).join(Post.author).where(User.username == session["user"]))
    return render_template("dashboard.html", posts=posts)


@admin_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author_id = session["user_id"]
        pub_date = datetime.strptime(request.form.get("pub_date"), "%Y-%m-%d").date()
        post = Post(title=title, content=content, pub_date=pub_date, author_id=author_id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("new.html", today=date.today().strftime("%Y-%m-%d"))


@admin_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = db.get_or_404(Post, post_id, description="Article not found")
    published = post.pub_date <= date.today()
    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        if not published:
            post.pub_date = datetime.strptime(request.form.get("pub_date"), "%Y-%m-%d").date()
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("edit.html", post=post, published=published)


@admin_bp.route("/delete/<int:post_id>")
@login_required
def delete(post_id):
    db.session.get
    post = db.get_or_404(Post, post_id, description="Article not found")
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/preview/<int:post_id>")
def preview(post_id):
    post = db.get_or_404(Post, post_id, description="Article not found")
    return render_template("article.html", post=post)
