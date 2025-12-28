"""Default configuration for the Flask application.

Store small, non-sensitive defaults here. For production, override values via
an instance config file or environment variables.
"""


class DefaultConfig:
    """Default configuration values used by the Flask app.

    SECRET_KEY should be overridden in production.
    """
    SECRET_KEY = "3497942ef71002df64c973329f6eeaa7ff515873215d56f002768ab650a2e89a"
    SQLALCHEMY_DATABASE_URI = "sqlite:///blog.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
