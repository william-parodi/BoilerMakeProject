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
conversation_history = []  # Holds chat history per session

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
    """Update the memory with the new fact(s)."""
    memory_data = load_memory()

    key = "human_facts" if section == "human" else "agent_facts"

    # Split into multiple facts if necessary
    facts = re.split(r", and |\. |\n|, ", memory)
    for fact in facts:
        fact = fact.strip()
        if fact and fact not in memory_data[key]:
            memory_data[key].append(fact)

    save_memory(memory_data)

    return f"Memory updated. Current {section}_facts: {memory_data[key]}"

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
    4. Return the final assistant message and update `convo_ended` if the order is finalized.
    """
    memory_data = load_memory()
    convo_ended = False  # Initialize conversation state

    system_prompt = (
        "You are a chatbot with memory. You provide information about different topics to the user, and to be inquisitive. "
        "Specifically, you are designed to assist a user in ordering pizza. You hear their order, ask for clarifications, and finalize the order. "
        "A final order must include: 'size', 'crust', and 'quantity'. "
        "You must provide a human-readable response to the user, as if it is a normal conversation. "
        "If they don't specify any of those parameters, you must ask them for it. "
        "Whenever the user provides new info, you MUST call the 'core_memory_save' function. "
        "After you do so, provide your final answer to the user. "
        "When the final order is confirmed, include the phrase 'Finalized Order' in your response. "
        "This phrase indicates that the order is complete and the conversation has ended."
        "\nIf no new info is provided, respond without calling the function."
        "\nImportant: If multiple facts are provided, store them all."   
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

    choice = response.choices[0].message

    # Detect function calls and update memory
    if hasattr(choice, "tool_calls") and choice.tool_calls:
        for tool_call in choice.tool_calls:
            if tool_call.function.name == "core_memory_save":
                args = json.loads(tool_call.function.arguments)
                result_text = core_memory_save(**args)
                tool_response_message = {
                    "role": "function",
                    "name": tool_call.function.name,
                    "content": result_text
                }
                messages.append(tool_response_message)

        # Ask for the final assistant response after memory update
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        final_text = final_response.choices[0].message.content

    else:
        final_text = choice.content

    # **Check if the conversation has ended**
    if "Finalized Order" in final_text:
        convo_ended = True  # Mark conversation as ended

    return final_text, convo_ended
