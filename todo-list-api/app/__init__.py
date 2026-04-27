"""Application factory and top-level Flask `app` object.

This module creates the Flask `app` and loads configuration from
environment and an optional `instance/config.json` file. The instance
config is loaded if present; JSON errors or a missing file are ignored
but other exceptions will surface.
"""

import json

from flask import Flask

from app.config import DefaultConfig
from app.cli import init_db, clean_refresh_tokens


app = Flask(__name__, instance_relative_config=True)
app.config.from_object(DefaultConfig)
try:
    app.config.from_file("config.json", load=json.load, silent=True)
except json.JSONDecodeError:
    # Invalid instance config is non-fatal; keep defaults.
    pass
app.cli.add_command(init_db)
app.cli.add_command(clean_refresh_tokens)
print(app.config["RATELIMIT_STORAGE_URI"])

# Import views after extensions are initialized to avoid import-time side-effects
from app import views  # noqa: E402, F401
