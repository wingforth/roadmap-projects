# Personal Blog (Flask Example)

A minimal personal blog built with Flask and SQLite. This example demonstrates a simple admin interface (login, create/edit/delete posts), public views for published posts, and a small set of Flask CLI commands to manage the database and users.

## Features

- Create, edit, delete, preview posts
- Admin login using Flask sessions
- SQLite backend (blog.db)
- CLI commands: init-db, add-user, list-user, change-password, delete-user
- Simple templates and static CSS

## Requirements

- Python 3.8+
- Python packages (minimum): Flask, Flask-SQLAlchemy
- git
- Recommended: [uv](https://github.com/astral-sh/uv)

## Installation

1. Clone this repository git:

   ```sh
   git clone https://github.com/wingforth/roadmap-projects
   cd roadmap-projects/personal-blog
   ```

2. Create a virtual environment and install dependencies (uv required):

   ```sh
   uv sync
   ```

## Configuration

The application loads instance/config.json (instance-relative). Example file (instance/config.json):

```json
{
  "DEBUG": true,
  "SECRET_KEY": "replace-with-a-secure-random-string"
}
```

Notes:

- Ensure the `instance/` directory exists (the app will attempt to create it).
- Keep `SECRET_KEY` secret in production and set `DEBUG` to false in production.

## Database & CLI

This project uses SQLite with SQLAlchemy. The database file will be created in the working directory (sqlite:///blog.db).

Use the Flask CLI so the app factory is invoked and CLI commands are registered:

```sh
# Initialize database (drops and recreates tables)
flask --app "app:create_app" init-db

# Create a user (prompts for password)
flask --app "app:create_app" add-user <username>

# List users
flask --app "app:create_app" list-user

# Change a user's password (prompts for password)
flask --app "app:create_app" change-password <username>

# Delete a user (refuses if user has posts)
flask --app "app:create_app" delete-user <username>
```

Warning: `init-db` will drop existing tables.

Alternatively, for development you can run:

```sh
python run.py
```

but the Flask CLI approach is recommended when using the registered commands.

## Run the application

Development:

```sh
# Option A (run.py)
python run.py

# Option B (Flask CLI with reloader)
flask --app "app:create_app" run --reload
```

Default host: 127.0.0.1:5000 — open <http://127.0.0.1:5000>

## Routes and Usage

Public:

- GET / or /home — list published posts (post.pub_date <= today)
- GET /article/<post_id> — view a published post

Admin (login required):

- GET,POST /login — login form
- GET /logout — logout
- GET /admin — dashboard listing the current user's posts
- GET,POST /new — create a new post (set publish date)
- GET,POST /edit/<post_id> — edit a post (if already published, publish date becomes read-only)
- GET /delete/<post_id> — delete a post (client-side confirmation)
- GET /preview/<post_id> — preview a post regardless of publish date

Typical publish flow:

1. Create an admin user with `flask --app "app:create_app" add-user admin`.
2. Open /login and sign in.
3. Go to /admin → + New Post, provide title/content and a publish date (today by default), then publish.
4. Posts with pub_date <= today appear on the homepage.

## Project layout (key files)

- app/
  - \_\_init\_\_.py — app factory, blueprint & CLI registration
  - models.py — SQLAlchemy models (Post, User)
  - admin.py — admin views and authentication helpers
  - guest.py — public views
  - cli.py — click commands (init-db, add-user, ...)
  - templates/ — Jinja2 templates (base, home, article, login, dashboard, new, edit)
  - static/ — static assets (style.css)
- instance/
  - config.json — per-instance configuration (not for VCS)
- run.py — simple development server entrypoint
- README.md — this file

## Development notes & security

- Passwords are hashed with Werkzeug utilities.
- Sessions store the logged-in username under `session["username"]`.
- There is no migration tool integrated (no Alembic); changing models requires manual DB handling.
- For production, use a WSGI server (gunicorn, uWSGI) and ensure `DEBUG=false` and a secure `SECRET_KEY`.

## Troubleshooting

- "Article not found": ensure the post exists and its pub_date is not in the future for public view.
- CLI commands not found: run commands via `flask --app "app:create_app" ...` so the factory registers them.
- Database file location: `sqlite:///blog.db` points to a file named `blog.db` in the working directory.
