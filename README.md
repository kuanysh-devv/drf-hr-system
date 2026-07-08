# DRF HR System

## Docker deployment

Create the Docker environment file:

```bash
cp .env.docker.example .env.docker
```

Update `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and the database password before deploying outside your machine.

Build and start the stack:

```bash
docker compose up --build -d
```

The API will be available at:

```text
http://localhost:8000
```

Useful commands:

```bash
docker compose logs -f web
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py migrate
docker compose down
```

The Compose stack runs:

- `web`: Django served by Gunicorn.
- `db`: PostgreSQL.
- `redis`: Redis for cache and Celery.
- `minio`: object storage for generated DOCX files. Console: `http://localhost:9001`.
- `celery`: Celery worker.
- `celery-beat`: scheduled Celery tasks.

Application static files, media files, Postgres data, and Redis data are stored in Docker volumes.
