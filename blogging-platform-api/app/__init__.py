"""Application package for the blogging-platform-api.
"""

from flask import Flask

from app.config import DefaultConfig

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(DefaultConfig)
try:
    # Allow an optional instance config file without failing if it doesn't exist.
    app.config.from_pyfile("config.py", silent=True)
except Exception:
    # If loading fails for unexpected reasons, continue with defaults.
    pass

from app import views  # noqa: E402, F401
