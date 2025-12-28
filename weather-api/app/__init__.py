"""
Application factory for the weather app package.

This module exposes a small `create_app` helper that builds a Flask
application configured from :class:`app.config.Config` and environment
variables. The factory creates the instance folder, loads environment
variables from a .env file when present, and wires the WeatherApp
application helper (routes, cache and limiter) into the Flask app.
"""

import os
import logging
import logging.handlers

from flask import Flask
from dotenv import load_dotenv

from app import views, config


def set_logger(app: Flask) -> None:
    # Configure unified logging using Flask's logger. Keep the default level
    # configurable via `LOG_LEVEL` in instance config (fallback to INFO).
    log_level = app.config.get("LOG_LEVEL", "WARNING")
    try:
        level = getattr(logging, str(log_level).upper())
    except Exception:
        level = logging.WARNING

    # Configure a rotating file handler inside the instance folder so logs
    # are persisted per-deployment. File name, max size and backups can be
    # overridden via instance config.
    log_file_name = app.config.get("LOG_FILE_NAME", "log.txt")
    max_bytes = int(app.config.get("LOG_MAX_BYTES", 10 * 1024 * 1024))
    backup_count = int(app.config.get("LOG_BACKUP_COUNT", 5))

    log_path = os.path.join(app.instance_path, log_file_name)
    handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count)
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    # Remove default handlers to avoid duplicate logs in some WSGI setups
    for h in list(app.logger.handlers):
        app.logger.removeHandler(h)
    app.logger.addHandler(handler)

    app.logger.debug("Logger configured (level=%s)", logging.getLevelName(level))


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    try:
        load_dotenv(os.path.join(app.instance_path, ".env"))
    except FileNotFoundError:
        load_dotenv()

    app.config.from_object(config.Config())
    app.config.from_pyfile("config.py", silent=True)
    set_logger(app)
    views.register_routes(app)
    return app
