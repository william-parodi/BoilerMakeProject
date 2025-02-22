import openai
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("API_KEY")
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

def chatbot_agent(user_message):
    """
    1. Load memory.
    2. Send system instructions + memory + user message to LLM.
    3. If the LLM calls the memory tool, handle it, then ask the LLM to produce a final answer.
    4. Return the final assistant message.
    """
    memory_data = load_memory()

    system_prompt = (
        "You are a chatbot with memory. You provide information about different topics to the user, and to be inquisitve."
        "If the user asks you to do something, ask all the clarifying questions necessary to fulfill the user's request."
        "Whenever the user provides new info, you MUST call the 'core_memory_save' function. "
        "After you do so, provide your final answer to the user."
        "\nIf no new info is provided, respond without calling the function."
        "\nImportant: If multiple facts are provided, store them all."
    )

    memory_json = json.dumps(memory_data, indent=2)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": "[MEMORY]\n" + memory_json},
        {"role": "user", "content": user_message}
    ]

    # Make the first call to the API
    response = client.chat.completions.create(
        model="gpt-4o",   # Or your model of choice
        messages=messages,
        tools=[core_memory_save_metadata]
    )

    choice = response.choices[0].message

    # Check if the LLM decided to call the function
    if hasattr(choice, "tool_calls") and choice.tool_calls:
        # If there's at least one function call:
        for tool_call in choice.tool_calls:
            if tool_call.function.name == "core_memory_save":
                args = json.loads(tool_call.function.arguments)
                result_text = core_memory_save(**args)
                # Provide the tool result as a "function" role message
                # so the LLM can see what happened
                tool_response_message = {
                    "role": "function",
                    "name": tool_call.function.name,
                    "content": result_text
                }
                messages.append(tool_response_message)

        # After handling the function calls, we ask the model for its final answer
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return final_response.choices[0].message.content
    else:
        # No function calls => the LLM just gave a direct user-facing response
        return choice.content

if __name__ == "__main__":
    print("Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = chatbot_agent(user_input)
        print("Bot:", response)
