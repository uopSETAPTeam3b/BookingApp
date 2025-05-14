from fastapi.testclient import TestClient
import pytest
import os
from database import DatabaseManager

from app import app

client = TestClient(app)

if os.path.exists("database_test.db"):
    os.remove("database_test.db")

token = None
studentToken = None

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_404():
    response = client.get("/3209857820")
    assert response.status_code == 404
# ACCOUNT TESTS

# Test /login endpoint
def test_login():
    response = client.post("/account/login", json={"username": "up2211837@myport.ac.uk", "password": "welcome1234"})
    assert response.status_code == 200
    # Assert token is returned
    global token
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
    assert "bookings" in response.json()

def test_get_bookings_invalid_token():
    response = client.post("/booking/get_bookings", json={
        "token": "invalid_token"
    })
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"
"valid_token"

# Test /get_bookings_for_date endpoint
def test_get_bookings_for_date():
    response = client.get("/booking/get_bookings_for_date", params={
        "dateTime": 1683680400  # example timestamp
    })
    assert response.status_code == 200
    assert "bookings" in response.json()

# Test /get_day_bookings endpoint
def test_get_day_bookings():
    response = client.get("/booking/get_day_bookings", params={
        "booking_id": 1
    })
    assert response.status_code == 200
    assert "bookings" in response.json()

def test_get_day_bookings_invalid_booking():
    response = client.get("/booking/get_day_bookings", params={
        "booking_id": 999  # non-existent booking id
    })
    assert response.status_code == 404
    assert response.json().get("detail") == "Booking not found"

# Test /share endpoint
def test_share_room():
    response = client.post("/booking/share", json={
        "token": f"{token}",
        "booking_id": 1,
        "username": "other_user"
    })
    assert response.status_code == 200
    assert response.text == ""

def test_share_room_invalid_user():
    response = client.post("/booking/share", json={
        "token": "valid_token",
        "booking_id": 1,
        "username": "non_existent_user"
    })
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"
    
# Test /cancel endpoint
def test_cancel_booking():
    response = client.post("/booking/cancel", json={
        "token": f"{token}",
        "booking_id": 1
    })
    assert response.status_code == 200
    assert response.text == '"Booking cancelled"'

def test_cancel_booking_invalid_token():
    response = client.post("/booking/cancel", json={
        "token": "invalid_token",
        "booking_id": 1
    })
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"

def test_cancel_booking_not_found():
    response = client.post("/booking/cancel", json={
        "token": f"{token}",
        "booking_id": 999 
    })
    assert response.status_code == 404
    assert response.json().get("detail") == "Booking not found"

# Test /get_room endpoint
def test_get_room():
    response = client.post("/booking/get_room", json={
        "token": f"{token}",
        "room_id": 1
    })
    assert response.status_code == 200
    assert "name" in response.json()

def test_get_room_invalid_token():
    response = client.post("/booking/get_room", json={
        "token": "invalid_token",
        "room_id": 1
    })
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"

def test_get_room_not_found():
    response = client.post("/booking/get_room", json={
        "token": f"{token}",
        "room_id": 99  # non-existent room id
    })
    assert response.status_code == 404
    assert response.json().get("detail") == "Room not found"
    
# Test /logout user role endpoint
def test_logout():
    response = client.post("/account/logout", json={"token": token})
    assert response.status_code == 200
    assert response.text == '"Logout successful"'
    
# Test /register endpoint
def test_register():
    response = client.post("/account/register", json={"username": "user2", "password": "password"})
    assert response.status_code == 200
    token = response.json().get("token")
    assert len(token) == 64

def test_register_user_exists():
    # Try to register an existing user
    response = client.post("/account/register", json={"username": "up2211837@myport.ac.uk", "password": "welcome1234"})
    assert response.status_code == 400
    assert response.json().get("message") == "User already exists"

