from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_chat_service


class FakeChatService:

    model_name = "test-model"

    async def chat(self, message: str) -> str:
        return "This is a mocked AI response."


def get_test_chat_service() -> FakeChatService:
    return FakeChatService()


app.dependency_overrides[get_chat_service] = (get_test_chat_service)

client = TestClient(app)


def test_chat_success():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "What is machine learning?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["response"] == (
        "This is a mocked AI response."
    )

    assert data["model"] == "test-model"


def test_chat_empty_message():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": ""
        },
    )

    assert response.status_code == 422


def test_chat_missing_message():
    response = client.post(
        "/api/v1/chat",
        json={},
    )

    assert response.status_code == 422