from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_404():
    response = client.get("/3209857820")
    assert response.status_code == 404

def test_login():
    response = client.post("/account/login", json={"username": "", "password": ""})
    assert response.status_code == 200
    assert response.json() == {}
