from fastapi.testclient import TestClient
import pytest
import os
from database import DatabaseManager

from app import app

client = TestClient(app)

os.remove("database_test.db")

token = None

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_404():
    response = client.get("/3209857820")
    assert response.status_code == 404

def test_register():
    global token
    response = client.post("/account/register", json={"username": "user1", "password": "password"})
    assert response.status_code == 200

    # Should return token of length 64
    token = response.json()
    assert len(token) == 64

def test_logout():
    response = client.post("/account/logout", json={"token": token})
    assert response.status_code == 200

def test_login():
    global token
    response = client.post("/account/login", json={"username": "user1", "password": "password"})
    assert response.status_code == 200

    # Should return token of length 64
    token = response.json()
    assert len(token) == 64

def test_book():
    response = client.post("/booking/book", json={})
