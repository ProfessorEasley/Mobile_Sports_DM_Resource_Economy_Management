
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import engine
from backend.app.models import Base, User, Wallet
from sqlalchemy.orm import Session

client = TestClient(app)

# Dummy JWT or basic auth header for testing
AUTH_HEADER = {"Authorization": "Bearer testtoken"}

@pytest.fixture(autouse=True)
def setup_database():
    # Drop and recreate tables before each test for isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Seed test user and wallet
    with Session(bind=engine) as db:
        user = User(username="testuser", email="testuser@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
        wallet = Wallet(user_id=user.id, coins=100, gems=10, credits=50)
        db.add(wallet)
        db.commit()

def test_add_currency():
    response = client.post("/wallet/add", json={"currency_type": "coins", "amount": 100}, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert "coins" in data and data["coins"] >= 100

def test_spend_currency():
    response = client.post("/wallet/spend", json={"currency_type": "coins", "amount": 50}, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert "coins" in data and data["coins"] >= 0

def test_get_balance():
    response = client.get("/wallet/balance", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert all(k in data for k in ["coins", "gems", "credits"])

def test_spend_insufficient():
    response = client.post("/wallet/spend", json={"currency_type": "gems", "amount": 999999}, headers=AUTH_HEADER)
    assert response.status_code == 400

def test_display_wallet():
    response = client.get("/wallet/display", headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == "1"
    assert data["coins"] == pytest.approx(100)
    assert data["gems"] == pytest.approx(10)
    assert data["credits"] == pytest.approx(50)

def test_display_wallet_by_username():
    response = client.get("/wallet/display", params={"player_id": "testuser"}, headers=AUTH_HEADER)
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == "testuser"
    assert data["coins"] == pytest.approx(100)
    assert data["gems"] == pytest.approx(10)
    assert data["credits"] == pytest.approx(50)
