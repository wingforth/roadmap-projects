import os
import json
from flask import Flask, current_app
from .guest import guest_bp
from .admin import admin_bp
from .cli import init_db, add_user, list_user, delete_user, change_password, db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///blog.db")
    app.config.from_file("config.json", load=json.load, silent=True)
    app.register_blueprint(guest_bp)
    app.register_blueprint(admin_bp)
    db.init_app(app)
    with app.app_context():
        current_app.cli.add_command(init_db)
        current_app.cli.add_command(add_user)
        current_app.cli.add_command(list_user)
        current_app.cli.add_command(delete_user)
        current_app.cli.add_command(change_password)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    return app
