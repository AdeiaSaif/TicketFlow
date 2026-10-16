from fastapi.testclient import TestClient
from main import app
from rag import service

client = TestClient(app)


def test_ask_returns_answer_and_sources(monkeypatch):
    # Mistral API ko call kiye baghair fake jawab
    def fake_generate_text(question):
        return {"answer": "Refunds take 5 to 7 working days.", "sources": [3]}

    monkeypatch.setattr(service, "generate_text", fake_generate_text)

    response = client.post("/ask/", json={"question": "How long do refunds take?"})

    assert response.status_code == 200
    assert response.json() == {"answer": "Refunds take 5 to 7 working days.", "sources": [3]}


def test_ask_empty_question_returns_400():
    response = client.post("/ask/", json={"question": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty"
