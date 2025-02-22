def test_process_pizzas(client_instance, mock_openai):
    request_data = {
        "pizzas": [
            {"quantity": 2, "size": "medium", "crust": "thin"}
        ]
    }
    response = client_instance.post("/pizzas", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "pizzas" in data
    assert isinstance(data["pizzas"], list)
    assert "additional_info" in data
