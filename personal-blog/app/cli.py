import click
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from .models import db, User, Post


@click.command("init-db")
def init_db() -> None:
    db.drop_all()
    db.create_all()
    print("Initialize database successfully.")


@click.command("add-user")
@click.argument("username", required=True)
@click.option("--password", hide_input=True, prompt="enter password")
def add_user(username, password) -> None:
    db.session.add(User(username=username, password_hash=generate_password_hash(password)))
    db.session.commit()
    print(f"Create user ({username}) successfully.")


@click.command("list-user")
def list_user() -> None:
    usernames = db.session.scalars(select(User.username))
    print("Users\n-----")
    for user in usernames:
        print(user)


@click.command("change-password")
@click.argument("username", required=True)
@click.option("--password", hide_input=True, prompt="enter password")
def change_password(username, password) -> None:
    user = db.session.scalars(select(User).where(User.username == username)).one_or_none()
    if user is None:
        print(f"invalid user: {username}")
        return
    user.password_hash = generate_password_hash(password)
    db.session.commit()
    print(f"Change password for user ({username}) successfully.")


@click.command("delete-user")
@click.argument("username", required=True)
def delete_user(username) -> None:
    user = db.session.scalars(select(User).where(User.username == username)).one_or_none()
    if user is None:
        print(f"Invalid user: {username}")
        return
    posts = db.session.scalars(select(Post).where(Post.author == user.username)).all()
    if posts:
        print("Failed: can't delete a user that has posts in database.")
        return
    db.session.delete(user)
    db.session.commit()
    print(f"Delete user ({username}) successfully.")
