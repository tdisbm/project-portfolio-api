.PHONY: install dev migrate makemigrations shell superuser test test-coverage lint format typecheck run-wsgi run-asgi certs seed

install:
	uv sync --all-groups

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

shell:
	uv run python manage.py shell

superuser:
	uv run python manage.py createsuperuser

seed-projects:
	uv run python manage.py seed_projects $(if $(n),--count $(n),)

test:
	uv run python -m pytest

test-coverage:
	uv run python -m pytest --cov=apps --cov-report=term-missing

lint:
	uv run ruff check .

format:
	uv run ruff format .

run-wsgi:
	uv run gunicorn config.wsgi:application \
		--bind 0.0.0.0:8000 \
		--workers 4 \
		--worker-class sync \
		--log-level info

run-asgi:
	uv run uvicorn config.asgi:application \
		--host 0.0.0.0 \
		--port 8000 \
		--workers 4 \
		--log-level info

certs-localhost:
	mkcert -install
	mkcert -key-file docker/certs/localhost.key -cert-file docker/certs/localhost.crt localhost 127.0.0.1
