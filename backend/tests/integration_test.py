import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") in {"", "dummy_api_key_for_testing"},
    reason="Real OpenAI API key not provided; skipping integration tests."
)
def test_process_chat_real_api():
    request_data = {"user_input": "I would like 2 large pizzas with thick crust."}
    response = client.post("/chat", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "pizzas" in data
    assert isinstance(data["pizzas"], list)
    assert "additional_info" in data
