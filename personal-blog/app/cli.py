"""CLI commands for database and user/post management.

Commands:
  - init-db
  - create-db
  - delete-db
  - add-user
  - list-user
  - list-post
  - change-password
  - delete-user
"""

import click
from sqlalchemy import select, func
from werkzeug.security import generate_password_hash

from app.models import db, User, Post


@click.command("init-db")
def init_db() -> None:
    """Drop all tables and recreate them (development helper)."""
    db.drop_all()
    db.create_all()
    print("Initialize database successfully.")


@click.command("create-db")
def create_db() -> None:
    """Create database tables if they do not exist."""
    db.create_all()
    print("Create database successfully.")


@click.command("delete-db")
def delete_db() -> None:
    """Drop all database tables."""
    db.drop_all()
    print("Delete database successfully.")


@click.command("add-user")
@click.argument("username", required=True)
@click.option("--password", hide_input=True, prompt="enter password")
def add_user(username, password) -> None:
    """Create a new user; abort if username already exists."""
    exists = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if exists:
        print(f"User {username} already exists.")
        return

    db.session.add(User(username=username, password_hash=generate_password_hash(password)))
    db.session.commit()
    print(f"Create user ({username}) successfully.")


@click.command("list-user")
def list_user() -> None:
    """List all usernames in the database."""
    usernames = db.session.scalars(select(User.username))
    print("Users\n-----")
    for user in usernames:
        print(user)


@click.command("list-post")
@click.option("--user", default=None)
def list_post(user) -> None:
    """List posts; optional --user filter to list only posts by username."""
    query = select(Post)
    if user:
        # join Post.author to filter by username
        query = query.join(Post.author).where(User.username == user)

    posts = db.session.scalars(query)
    fmt = "{:<4} {:30} {:20} {}"
    print(fmt.format("id", "title", "author", "pub_date"))
    print(fmt.format("--", "-----", "------", "--------"))
    for post in posts:
        author_name = post.author.username if post.author else "<unknown>"
        print(fmt.format(post.id, post.title[:30], author_name[:20], post.pub_date))


@click.command("change-password")
@click.argument("username", required=True)
@click.option("--password", hide_input=True, prompt="enter password")
def change_password(username, password) -> None:
    """Change a user's password (hashes with Werkzeug)."""
    user = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None:
        print(f"User {username} does not exist.")
        return

    user.password_hash = generate_password_hash(password)
    db.session.commit()
    print(f"Password for {username} updated.")


@click.command("delete-user")
@click.argument("username", required=True)
def delete_user(username) -> None:
    """Delete a user; prompt if user has posts (confirm before deleting)."""
    user = db.session.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None:
        print(f"User {username} does not exist.")
        return

    post_count = db.session.scalar(select(func.count()).select_from(Post).where(Post.author_id == user.id))
    if post_count:
        if not click.confirm(
            f'User "{username}" has {post_count} post(s). Delete the user and all associated posts?', default=False
        ):
            print("Cancelled.")
            return

    db.session.delete(user)
    db.session.commit()
    print(f"Delete user ({username}) successfully.")
