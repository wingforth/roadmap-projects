"""Default configuration for the Flask application.

Store small, non-sensitive defaults here. For production, override values via
an instance config file or environment variables.
"""

import os


class DefaultConfig:
    """Default configuration values used by the Flask app.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///blog.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
