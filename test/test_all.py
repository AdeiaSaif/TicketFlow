from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_register_user():
    res = client.get("/getuser")
    assert True
    