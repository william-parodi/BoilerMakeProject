import os
import pytest
import logging
from fastapi.testclient import TestClient
from app.main import app

# Setup logger
logger = logging.getLogger("pizza_app")
logger.setLevel(logging.DEBUG)  # Log at DEBUG level

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

client = TestClient(app)

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") in {"", "dummy_api_key_for_testing"},
    reason="Real OpenAI API key not provided; skipping integration tests."
)
def test_process_chat_real_api():
    request_data = {"user_input": "I would like 2 large pizzas with hand tossed crust."}
    response = client.post("/chat", json=request_data)
    
    print("\n ChatGPT Response:", response.text)
    logger.info(f"ChatGPT Response: {response.text}")

    assert response.status_code == 200
    data = response.json()
    assert "pizzas" in data
    assert isinstance(data["pizzas"], list)
    assert "additional_info" in data
