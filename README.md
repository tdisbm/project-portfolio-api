# Project Portfolio

A full-stack portfolio application for managing personal projects. The backend exposes a REST API built with Django, and the frontend is an Angular SPA styled with Angular Material. Everything runs behind an nginx reverse proxy with HTTPS.

---

## Architecture

```
Browser
  └── nginx gateway (HTTPS :443)
        ├── /api/*  → Django backend  (:8000)
        └── /*      → Angular frontend (:80)
```

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | Angular 21, Angular Material      |
| Backend   | Django 5.2, Python 3.12, Gunicorn |
| Database  | PostgreSQL 17                     |
| Gateway   | nginx (TLS termination)           |
| Packaging | uv (backend), npm (frontend)      |

---

## Prerequisites

| Tool                | Minimum version | Notes                                          |
|---------------------|-----------------|------------------------------------------------|
| Docker Engine       | 20.10           | Required for `condition: service_healthy`      |
| Docker Compose      | V2 (plugin)     | Use `docker compose`, not `docker-compose`     |
| mkcert              | any             | Only needed to regenerate the TLS certificates |

> **Docker Desktop** (Mac/Windows) ships both Docker Engine and Compose V2 out of the box. On Linux, install the [Compose plugin](https://docs.docker.com/compose/install/linux/).

---

## Quick Start

### 1. Generate TLS certificates (first time only)

The repo ships with pre-generated certificates for `localhost`. If you need to regenerate them:

```bash
# Install mkcert (https://github.com/FiloSottile/mkcert)
make certs-localhost
```

### 2. Start the stack

```bash
docker compose up --build
```

On first start, Django migrations run automatically before the server comes up.

### 3. Create your first user

```bash
docker compose exec project-portfolio-api uv run python manage.py createsuperuser
```

Alternatively, register directly through the UI at **https://localhost/register**.

### 4. Open the app

**https://localhost** — your browser will warn about the self-signed certificate; accept it to proceed.

---

## Stopping and restarting

```bash
# Stop without removing data
docker compose stop

# Stop and remove containers (data volume is preserved)
docker compose down

# Stop and wipe everything including the database volume
docker compose down -v
```

---

## Environment Variables

| Variable                 | Default                      | Required | Description                                    |
|--------------------------|------------------------------|----------|------------------------------------------------|
| `SECRET_KEY`             | —                            | Yes      | Django secret key                              |
| `ALLOWED_HOSTS`          | `localhost,127.0.0.1`        | No       | Comma-separated list of allowed hostnames      |
| `DB_NAME`                | `portfolio-app`              | No       | PostgreSQL database name                       |
| `DB_USER`                | `portfolio-app-user`         | No       | PostgreSQL user                                |
| `DB_PASSWORD`            | `hackme`                     | No       | PostgreSQL password                            |
| `DB_HOST`                | `postgres`                   | No       | PostgreSQL host                                |
| `DB_PORT`                | `5432`                       | No       | PostgreSQL port                                |
| `DJANGO_SETTINGS_MODULE` | `config.settings.development`| No       | Settings module to use                         |

---

## API Endpoints

All endpoints are prefixed with `/api/`.

### Auth

| Method | Path                | Auth required | Description            |
|--------|---------------------|---------------|------------------------|
| POST   | `/api/auth/register/` | No          | Register a new account |
| POST   | `/api/auth/login/`    | No          | Obtain a Bearer token  |
| POST   | `/api/auth/logout/`   | Yes         | Revoke the current token |
| GET    | `/api/auth/me/`       | Yes         | Get the current user   |

Authentication uses `Authorization: Bearer <token>` on all protected routes.

### Projects

| Method       | Path                        | Description                  |
|--------------|-----------------------------|------------------------------|
| GET          | `/api/projects/`            | List projects (filterable)   |
| POST         | `/api/projects/create/`     | Create a project             |
| GET          | `/api/projects/<id>/`       | Retrieve a project           |
| PATCH        | `/api/projects/<id>/update/`| Update a project             |
| DELETE       | `/api/projects/delete/<id>/`| Delete a project             |

#### List query parameters

| Parameter           | Type   | Description                                 |
|---------------------|--------|---------------------------------------------|
| `name`              | string | Case-insensitive name filter                |
| `description`       | string | Case-insensitive description filter         |
| `technology`        | string | Filter by technology (repeatable, OR logic) |
| `date_start_after`  | date   | `YYYY-MM-DD` — start date ≥ value           |
| `date_end_before`   | date   | `YYYY-MM-DD` — end date ≤ value             |
| `order_by_name`     | string | `asc` or `desc`                             |
| `order_by_date_start` | string | `asc` or `desc`                           |
| `order_by_date_end` | string | `asc` or `desc`                             |
| `page`              | int    | Page number (default: 1)                    |
| `page_size`         | int    | Results per page (default: 10)              |

---

## Local Development (without Docker)

You need Python 3.12+, [uv](https://github.com/astral-sh/uv), Node 22+, and a running PostgreSQL instance.

### Backend

```bash
# Install dependencies
make install

# Copy and edit environment config
cp .env.example .env   # or create .env manually (see above)

# Apply migrations
make migrate

# Create a superuser
make superuser

# Start the dev server (http://localhost:8000)
uv run python manage.py runserver
```

### Frontend

```bash
cd frontend/project-portfolio-app

npm install

# Start the dev server (http://localhost:4200)
npm start
```

When running locally, point the Angular environment at the Django dev server by setting `apiUrl` in `src/environments/environment.ts`.

### Available `make` targets

| Target                    | Description                                      |
|---------------------------|--------------------------------------------------|
| `make install`            | Install all Python dependencies (uv sync)        |
| `make migrate`            | Apply pending migrations                         |
| `make makemigrations`     | Generate new migrations                          |
| `make shell`              | Open the Django interactive shell                |
| `make superuser`          | Create a Django superuser                        |
| `make test`               | Run the test suite with pytest                   |
| `make test-coverage`      | Run tests with coverage report (term-missing)    |
| `make seed-projects`      | Seed 10 random projects for TESTUSER             |
| `make seed-projects n=50` | Seed N random projects for TESTUSER              |
| `make lint`               | Check code style with Ruff                       |
| `make format`             | Auto-format code with Ruff                       |
| `make run-wsgi`           | Start Gunicorn WSGI server (4 workers, port 8000)|
| `make run-asgi`           | Start Uvicorn ASGI server (4 workers, port 8000) |
| `make certs-localhost`    | Regenerate TLS certificates for localhost        |

### Seeding test data

```bash
# Create 10 random projects linked to TESTUSER / TESTUSER (default)
make seed-projects

# Create a specific number of projects
make seed-projects n=50
```

If the `TESTUSER` account does not exist it is created automatically. Running the command again only adds more projects — the existing user is never overwritten.

---

## Testing

### Run the suite

```bash
# Run the full suite
make test

# Run with coverage report
make test-coverage

# Unit tests only (no database required)
uv run pytest tests/unit
```

### Test structure

```
tests/
├── conftest.py                       # Shared fixtures (user, token, auth_client, make_project)
├── test_core.py                      # Health-check and index endpoints
├── test_auth.py                      # Integration: register, login, logout, me (13 tests)
├── test_projects.py                  # Integration: project CRUD, filters, ordering, pagination,
│                                     #   cross-user isolation (23 tests)
└── unit/
    ├── test_user_serializers.py      # validate_register_data, serialize_user (11 tests)
    ├── test_project_serializers.py   # validate_project_data, serialize_project (14 tests)
    ├── test_require_auth.py          # require_auth decorator (7 tests)
    └── test_queryable.py             # @queryable decorator: pagination, filtering, ordering (13 tests)
```

Integration tests use Django's test `Client` with a real SQLite database. Unit tests use `RequestFactory` or plain function calls and mock only the token repository where needed.

---

## Project Structure

```
project-portfolio-api/
├── apps/
│   ├── core/           # Shared models (TimeStampedModel), middleware, health check
│   ├── project/        # Project CRUD, filtering/ordering decorator
│   └── users/          # Authentication (AuthToken), login/register/logout endpoints
├── config/
│   ├── settings/       # base.py, development.py, production.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── docker/
│   ├── nginx/          # nginx.conf (TLS + reverse proxy)
│   └── certs/          # TLS certificates for localhost
├── frontend/
│   └── project-portfolio-app/   # Angular SPA
│       ├── src/app/
│       │   ├── guards/          # authGuard (route protection)
│       │   ├── interceptors/    # authInterceptor (Bearer token injection)
│       │   ├── models/          # TypeScript interfaces
│       │   ├── pages/           # home, login, register, project-list
│       │   ├── services/        # AuthService, ProjectService
│       │   └── shared/          # Dialogs (form, confirm)
│       └── Dockerfile           # Multi-stage: node build → nginx serve
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── pyproject.toml
```

## Known issues
1. Security is very basic. No password reset, no email confirmation, no two-factor authentication. The implementation is not production-ready and only serves as a demonstration of the project
2. The frontend is not fully responsive, like it is written by a backend software engineer
3. No strict validation of the input data
4. Frontend project MUST be outside the `frontend/` directory. Ideally in a separate repo. Put it there for the showcase only
