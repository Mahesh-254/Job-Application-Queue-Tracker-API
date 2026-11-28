import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DB_URL = "sqlite:///./test_tracker.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def get_auth_headers():
    client.post(
        "/register",
        json={"username": "testuser", "password": "strongpassword", "role": "reviewer"},
    )
    login_res = client.post(
        "/login",
        data={"username": "testuser", "password": "strongpassword"},
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_unauthenticated_access_blocked():
    res = client.get("/applications")
    assert res.status_code == 401


def test_full_application_lifecycle_and_duplicate_block():
    headers = get_auth_headers()
    payload = {
        "client_name": "Mahesh",
        "company_name": "Stripe",
        "role_title": "Backend Engineer",
        "status": "Submitted",
    }

    # Create
    create_res = client.post("/applications", json=payload, headers=headers)
    assert create_res.status_code == 201
    app_id = create_res.json()["id"]

    # Duplicate check returns 409
    dup_res = client.post("/applications", json=payload, headers=headers)
    assert dup_res.status_code == 409

    # Update status via PATCH
    patch_res = client.patch(
        f"/applications/{app_id}",
        json={"status": "Interview"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "Interview"

    # Stats summary
    stats_res = client.get("/applications/stats/summary", headers=headers)
    assert stats_res.status_code == 200
    assert stats_res.json()["total_applications"] == 1
    assert stats_res.json()["status_breakdown"]["Interview"] == 1

    # Delete
    del_res = client.delete(f"/applications/{app_id}", headers=headers)
    assert del_res.status_code == 204