from fastapi.testclient import TestClient
from main import app
import pytest
from auth2 import get_current_user
client = TestClient(app)

class MockUser:
    id = 1

def override_get_current_user():
    return MockUser()

app.dependency_overrides[get_current_user] = override_get_current_user
def test_register_user():
    response = client.get("/getuser")
    assert "data" in response.json()
    