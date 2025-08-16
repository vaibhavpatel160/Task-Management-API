# Task Management API (FastAPI + PostgreSQL + Redis + Docker)

A production-ready starter that mirrors the stack in your resume:
- **FastAPI** for the REST API
- **PostgreSQL** with **SQLAlchemy ORM**
- **JWT** auth (access tokens) using `python-jose`
- **Redis** caching for read-heavy endpoints
- **Docker Compose** for one-command local run
- **CI-friendly testing** with `pytest` and FastAPI `TestClient`

## Quickstart

### 1) Environment
Copy and edit `.env.example` → `.env` (sensible defaults provided).

### 2) Run with Docker
```bash
docker compose up --build
```
The API will be available at: http://localhost:8000  (docs at `/docs`)

### 3) Run locally (without Docker)
Make sure PostgreSQL and Redis are running and env variables are exported.
```bash
python -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4) Testing
```bash
pytest -q
```

## Features

- Register/Login with hashed passwords.
- CRUD for tasks (title, description, status, due_date) scoped to the authenticated user.
- Pagination + basic Redis caching on list/read routes (invalidated on writes).
- Input/output validation via Pydantic models.
- Sensible project layout, ready to extend (e.g., Alembic migrations later).

## Default Accounts (for quick test)
- You can register yourself at `/auth/register`, then login at `/auth/login` to get a bearer token.

## .env variables
See `.env.example` for all options. The Docker compose uses these automatically.

## Notes
- This project uses **synchronous SQLAlchemy sessions** with FastAPI (simple and robust).
- Consider adding **Alembic** for migrations once your schema stabilizes.
