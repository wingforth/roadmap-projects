"""CLI helpers for the application.

The `init-db` command creates all database tables. It runs inside the
Flask application context so extensions (like SQLAlchemy) are available.
"""

from datetime import datetime, UTC

import click
from sqlalchemy import delete

from app.models import db
from app.models import RefreshToken


@click.command("init-db")
def init_db():
    """Create database tables.

    This is intended to be run via `flask init-db` during development.
    """
    db.create_all()
    click.echo("Initialized the database.")


@click.command("clean-refresh-tokens")
def clean_refresh_tokens():
    """Remove revoked refresh tokens that have expired from the database.

    Useful to run as a periodic maintenance task.
    """
    now = datetime.now(tz=UTC)
    db.session.execute(delete(RefreshToken).where(RefreshToken.revoked.is_(True), RefreshToken.expires_at < now))
    db.session.commit()
    click.echo("Removed expired revoked refresh tokens.")
