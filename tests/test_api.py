import os
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import Base, engine, SessionLocal
from sqlalchemy.orm import Session

# Create tables for test (uses the same DB as configured; in CI you can point to a test DB)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_register_and_login_and_crud():
    # Register
    r = client.post("/auth/register", json={"email": "user@example.com", "password": "secret123", "full_name": "User"})
    assert r.status_code in (200, 201)

    # Login
    r = client.post("/auth/login", json={"email": "user@example.com", "password": "secret123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create task
    r = client.post("/tasks/", headers=headers, json={"title": "First Task", "description": "do it"})
    assert r.status_code == 201
    task_id = r.json()["id"]

    # Get task
    r = client.get(f"/tasks/{task_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "First Task"

    # List tasks
    r = client.get("/tasks/?limit=5", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # Update
    r = client.patch(f"/tasks/{task_id}", headers=headers, json={"status": "done"})
    assert r.status_code == 200
    assert r.json()["status"] == "done"

    # Delete
    r = client.delete(f"/tasks/{task_id}", headers=headers)
    assert r.status_code == 204
