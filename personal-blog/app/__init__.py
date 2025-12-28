import os
import json
from flask import Flask
from app.guest import guest_bp
from app.admin import admin_bp
from app.models import db
from app.cli import init_db, create_db, delete_db, add_user, list_user, delete_user, change_password, list_post


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///blog.db")
    app.config.from_file("config.json", load=json.load, silent=True)
    app.register_blueprint(guest_bp)
    app.register_blueprint(admin_bp)
    app.cli.add_command(init_db)
    app.cli.add_command(create_db)
    app.cli.add_command(delete_db)
    app.cli.add_command(init_db)
    app.cli.add_command(add_user)
    app.cli.add_command(list_user)
    app.cli.add_command(delete_user)
    app.cli.add_command(change_password)
    app.cli.add_command(list_post)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
