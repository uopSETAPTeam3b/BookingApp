from fastapi.testclient import TestClient
import pytest
import os
from database import DatabaseManager

from app import app

client = TestClient(app)

if os.path.exists("database_test.db"):
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
    token = response.json().get("token")
    assert len(token) == 64

def test_login_invalid_user():
    response = client.post("/account/login", json={"username": "invalid_user", "password": "password"})
    assert response.status_code == 401
    assert response.json().get("message") == "Invalid username or password"

# Test /me endpoint
def test_me():
    response = client.get(f'/account/me?token={token}')
    assert response.status_code == 200
    assert "username" in response.json()

def test_me_invalid_token():
    invalid_token = "invalid_token"
    response = client.get(f'/account/me?token={invalid_token}')
    assert response.status_code == 401
    assert response.json().get("message") == "Invalid token"

# Test /accountDetails endpoint
def test_account_details():
    response = client.get(f"/account/accountDetails?token={token}")
    assert response.status_code == 200
    # Assumed the response contains account details
    assert "username" in response.json()

def test_account_details_invalid_token():
    invalid_token = "invalid_token"
    response = client.get(f"/account/accountDetails?token={invalid_token}")
    assert response.status_code == 401
    assert response.json().get("message") == "Invalid token"


# Test /get_unis endpoint
def test_get_unis():
    response = client.get("/account/get_unis")
    assert response.status_code == 200
    # Assuming response returns a list of universities
    assert isinstance(response.json(), list)


# BOOKING TESTS
# Test /book endpoint
def test_book_room():
    response = client.post("/booking/book", json={
        "token": f"{token}",
        "datetime": 1683680400, 
        "room_id": 1,
        "duration": 1
    })
    assert response.status_code == 200
    assert response.json().get("message") == "Room booked successfully"
    assert "booking_id" in response.json()

def test_book_room_invalid_token():
    response = client.post("/booking/book", json={
        "token": "invalid_token",
        "datetime": 1683680400,
        "room_id": 1,
        "duration": 1
    })
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"

def test_book_room_already_booked():
    response = client.post("/booking/book", json={
        "token": f"{token}",
        "datetime": 1683680400,  # timestamp already booked
        "room_id": 1,
        "duration": 1
    })
    assert response.status_code == 409
    assert response.json().get("detail") == "Room already booked"
    
# Test /get_bookings endpoint
def test_get_bookings():
    response = client.post("/booking/get_bookings", json={
        "token": f"{token}"
    })
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
