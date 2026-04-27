# Todo List API

Simple RESTful todo list API built with Flask, JWT-based authentication, and SQLAlchemy.

Features
- User registration and login (passwords are hashed)
- Access and refresh JWT tokens (refresh token revocation and rotation)
- Per-user CRUD operations for todo tasks
- Rate limiting via `flask-limiter`

Quickstart

1. Ensure Python and the project virtual environment are set up.
2. Set required environment variables (at least `JWT_SECRET_KEY`). Example on PowerShell:

```powershell
set JWT_SECRET_KEY=your-secret
```

3. Run the app in development:

```powershell
python run.py
```

Testing

Tests use `pytest`. Run tests from the project root:

```powershell
python -m pytest -q
```

Configuration

- `JWT_SECRET_KEY`: Required. Secret used to sign JWTs. Can be provided via the `JWT_SECRET_KEY` environment variable or in `instance/config.json`.
- `SECRET_KEY`: Optional. Flask's `SECRET_KEY`. If not provided, the value will fall back to `JWT_SECRET_KEY`.
- `SQLALCHEMY_DATABASE_URI`: Database connection string (default `sqlite:///blog.db`). Use this to switch to Postgres, MySQL, etc.
- `SQLALCHEMY_TRACK_MODIFICATIONS`: SQLAlchemy tracking flag, default `False`.
- `RATELIMIT_AUTH_LIMITS`: Rate limit rules for authentication endpoints (e.g. `/login`, `/register`). Default is `50/day, 20/hour`. Can be overridden with environment or instance config.
- `RATELIMIT_CRUD_LIMITS`: Rate limit rules for CRUD endpoints. Default is `500/day, 200/hour, 50/minute`.
- `RATELIMIT_STORAGE_URI`: Storage backend for rate limiting (for example Redis). Default is `redis://localhost:6379/0`.
- `JWT_ACCESS_EXPIRE_SECOND` / `JWT_REFRESH_EXPIRE_SECOND`: Default expiration times (in seconds) for access and refresh tokens.
- `TODO_PAGE_SIZE_DEFAULT`: Default page size of todos for list endpoints (for example `/todos`).

These settings may be supplied via environment variables or placed into `instance/config.json` (which overrides defaults).

API Endpoints & Examples

All endpoints accept and return JSON. Protected endpoints require the header `Authorization: Bearer <ACCESS_TOKEN>`.

- Register `/register` [POST]: Create a new user and return an `access_token` and `refresh_token`.

	Example request:

	```bash
	curl -X POST http://localhost:5000/register \
		-H "Content-Type: application/json" \
		-d '{"name":"Alice","email":"alice@example.com","password":"secret"}'
	```

	Success response (201):

	```json
	{"access_token":"<ACCESS>","refresh_token":"<REFRESH>"}
	```

- Login `/login` [POST]: Obtain tokens using `email` and `password`.

	Example request:

	```bash
	curl -X POST http://localhost:5000/login \
		-H "Content-Type: application/json" \
		-d '{"email":"alice@example.com","password":"secret"}'
	```

	Success response (200):

	```json
	{"access_token":"<ACCESS>","refresh_token":"<REFRESH>"}
	```

- Refresh `/refresh` [POST]: Exchange a `refresh_token` for a new `access_token` and a rotated `refresh_token`. The used refresh token is revoked.

	Example request:

	```bash
	curl -X POST http://localhost:5000/refresh \
		-H "Content-Type: application/json" \
		-d '{"refresh_token":"<REFRESH>"}'
	```

	Success response (200):

	```json
	{"access_token":"<ACCESS>","refresh_token":"<REFRESH>"}
	```

- Logout `/logout` [POST]: Revoke a refresh token (log out).

	Example request:

	```bash
	curl -X POST http://localhost:5000/logout \
		-H "Content-Type: application/json" \
		-d '{"refresh_token":"<REFRESH>"}'
	```

- Create task `/todos` [POST]: Protected. Create a task and return it (201).

	Example request:

	```bash
	curl -X POST http://localhost:5000/todos \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer <ACCESS>" \
		-d '{"title":"Buy milk","description":"2L of milk"}'
	```

	Success response (201):

	```json
	{
		"id": 1,
		"title": "Buy milk",
		"description": "2L of milk",
		"created_at": "2026-04-26T12:34:56+00:00",
		"updated_at": "2026-04-26T12:34:56+00:00"
	}
	```

- Update task `/todos/<id>` [PUT]: Protected. Update a task owned by the user.

	Example request:

	```bash
	curl -X PUT http://localhost:5000/todos/1 \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer <ACCESS>" \
		-d '{"title":"Buy almond milk"}'
	```

	Success response (200):

	```json
	{
		"id": 1,
		"title": "Buy milk",
		"description": "Buy almond milk",
		"created_at": "2026-04-26T12:34:56+00:00",
		"updated_at": "2026-04-26T12:34:56+00:00"
	}
	```

- Delete task `/todos/<id>` [DELETE]: Protected. Delete a task (204 No Content on success).

	Example request:

	```bash
	curl -X DELETE http://localhost:5000/todos/1 \
		-H "Authorization: Bearer <ACCESS>"
	```

- List tasks `/todos` [GET]: Protected. Supports pagination, filtering and sorting.

	Query parameters:
	- `page`: page number (default `1`)
	- `limit`: page size (default from `TODO_PAGE_SIZE_DEFAULT`)
	- `search`: free-text search against `title` and `description` (preferred) — also accepts `search` or legacy `filter`
	- `date`: inclusive date range in `YYYY-MM-DD` format separated by comma. If only a date provided, it filters that single day.
	- `sort`: sort by `createdAt` or `updatedAt`. 
	- `order`: `asc` or `desc` (default `asc`)

	Example request:

	```bash
	curl "http://localhost:5000/todos?page=1&limit=10&search=milk&sort=createdAt&order=desc" \
		-H "Authorization: Bearer <ACCESS>"
	```

	Success response (200):

	```json
	{"data":[{...}],"page":1,"limit":10,"total":1}
	```

For production use:
- Set `SQLALCHEMY_DATABASE_URI` to a production database.
- Use a shared `RATELIMIT_STORAGE_URI` (for example Redis) when running multiple instances.

