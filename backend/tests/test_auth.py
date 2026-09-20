import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database.database import Base, get_db

# In-memory SQLite using StaticPool so all connections share the same memory DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    # Setup fresh tables
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    # Teardown
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_register_user_success(client):
    payload = {
        "name": "Sarah Connor",
        "email": "sarah@cyberdyne.org",
        "password": "SecurePassword123!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "sarah@cyberdyne.org"
    assert data["user"]["name"] == "Sarah Connor"
    assert "password_hash" not in data["user"]


def test_register_duplicate_email(client):
    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "Password123!"
    }
    # First registration
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with same email
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_login_success(client):
    # Register first
    reg_payload = {
        "name": "Alex Smith",
        "email": "alex@example.com",
        "password": "MyPassword2026!"
    }
    client.post("/api/auth/register", json=reg_payload)

    # Login
    login_payload = {
        "email": "alex@example.com",
        "password": "MyPassword2026!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alex@example.com"


def test_login_invalid_password(client):
    reg_payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "CorrectPassword123!"
    }
    client.post("/api/auth/register", json=reg_payload)

    login_payload = {
        "email": "jane@example.com",
        "password": "WrongPassword!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_protected_me_endpoint(client):
    reg_payload = {
        "name": "Maya Lin",
        "email": "maya@example.com",
        "password": "Password456!"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    # Access /api/auth/me without token -> 401
    res_no_token = client.get("/api/auth/me")
    assert res_no_token.status_code == 401

    # Access /api/auth/me with token -> 200
    res_with_token = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_with_token.status_code == 200
    data = res_with_token.json()
    assert data["email"] == "maya@example.com"
    assert data["name"] == "Maya Lin"


def test_logout_endpoint(client):
    reg_payload = {
        "name": "David Miller",
        "email": "david@example.com",
        "password": "Password789!"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
