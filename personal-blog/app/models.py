from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str]
    author: Mapped[str] = mapped_column(nullable=False)
    pub_date: Mapped[date] = mapped_column(default=date.today)


class User(db.Model):
    username: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
