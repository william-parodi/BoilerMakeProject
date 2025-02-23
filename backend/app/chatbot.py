import openai
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

MEMORY_FILE = "memory.json"

def load_memory():
    """Load memory from disk (JSON). Fallback to default structure if not found."""
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Memory file must be a dict.")
            if "human_facts" not in data:
                data["human_facts"] = []
            if "agent_facts" not in data:
                data["agent_facts"] = []
            return data
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return {"human_facts": [], "agent_facts": []}

def save_memory(memory_data):
    """Persist memory back to JSON."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_data, f, indent=4)

def core_memory_save(section: str, memory: str):
    """
    Update the memory with the new fact(s).
    section: "human" or "agent"
    memory: textual facts to store
    """
    memory_data = load_memory()

    if section == "human":
        key = "human_facts"
    else:
        key = "agent_facts"

    # Example: split on ", and", ". ", or ", " to capture multiple facts
    facts = re.split(r", and |\. |\n|, ", memory)
    for fact in facts:
        fact = fact.strip()
        if fact and fact not in memory_data[key]:
            memory_data[key].append(fact)

    save_memory(memory_data)

    return f"Memory updated. Current {section}_facts: {memory_data[key]}"

# Define the function schema for the new OpenAI function-calling
core_memory_save_metadata = {
    "type": "function",
    "function": {
        "name": "core_memory_save",
        "description": "Save important info about the user or the agent.",
        "parameters": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "enum": ["human", "agent"],
                    "description": "Choose 'human' to save info about the user, 'agent' for itself."
                },
                "memory": {
                    "type": "string",
                    "description": "The memory content to save."
                }
            },
            "required": ["section", "memory"]
        }
    }
}

async def chatbot_agent(user_message):
    """
    Ensure the response is a structured JSON with 'pizzas' and 'additional_info'.
    """
    memory_data = load_memory()

    system_prompt = (
        "You are a pizza ordering assistant. Your job is to extract the details into a JSON object "
        "with a 'pizzas' key (a list of pizza orders) and an 'additional_info' field for any extra information. "
        "Each pizza order should include 'quantity' (a positive integer), 'size' (small, medium, large), and 'crust' (thin, thick, stuffed). "
        "Discard any invalid orders. Do not return conversational responses. "
        "Return ONLY valid JSON. Do NOT return any additional explanations or text, just the JSON object."
    )

    memory_json = json.dumps(memory_data, indent=2)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": "[MEMORY]\n" + memory_json},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[core_memory_save_metadata]
    )

    if not hasattr(response, "choices") or not response.choices:
        raise ValueError("Invalid response received from OpenAI API.")

    raw_response = response.choices[0].message.content

    try:
        parsed_response = json.loads(raw_response)  # Ensure it's valid JSON
        if "pizzas" not in parsed_response:
            raise ValueError("Missing 'pizzas' key in response.")
        return parsed_response
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON response: {raw_response}")



if __name__ == "__main__":
    print("Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = chatbot_agent(user_input)
        print("Bot:", response)
