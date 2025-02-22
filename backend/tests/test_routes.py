import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.services import client  # Import OpenAI client from services.py

test_client = TestClient(app)  # Avoid conflict with imported `client`

@pytest.fixture
def client_instance():
    return test_client

@pytest.fixture
def mock_openai():
    with patch.object(client.chat.completions, "create", new_callable=AsyncMock) as mock_api:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"pizzas": [{"quantity": 2, "size": "medium", "crust": "hand tossed"}], "additional_info": "Extra info processed."}'))
        ]
        mock_api.return_value = mock_response
        yield mock_api

def test_process_chat_valid(client_instance, mock_openai):
    request_data = {
        "user_input": "I would like 2 medium pizzas with hand tossed crust."
    }
    response = client_instance.post("/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "pizzas" in data
    assert isinstance(data["pizzas"], list)
    assert "additional_info" in data

def test_process_chat_invalid_json(client_instance, mock_openai):
    async def mock_invalid_json(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="This is not valid JSON"))]
        return mock_response

    mock_openai.side_effect = mock_invalid_json

    request_data = {"user_input": "I want 2 pizzas"}
    response = client_instance.post("/chat", json=request_data)

    assert response.status_code == 500
    detail = response.json().get("detail", "")

    assert "Expecting value" in detail or "Parsed data did not match expected schema" in detail

def test_process_chat_openai_error(client_instance, mock_openai):
    mock_openai.side_effect = Exception("OpenAI API error")

    request_data = {"user_input": "I want 2 pizzas"}
    response = client_instance.post("/chat", json=request_data)

    assert response.status_code == 500
    detail = response.json().get("detail", "")

    assert "OpenAI API error" in detail
