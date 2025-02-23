from app.logger import logger
from app.chatbot import chatbot_agent  # Importing your chatbot function
import openai
import os
import json

# Initialize OpenAI client with the same API key
api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key=api_key)

async def process_user_input(input_text: str) -> dict:
    """
    Calls your memory-enabled chatbot, then formats the response into structured JSON.
    """
    try:
        # Step 1: Get conversational response from memory-enabled chatbot
        chatbot_response, convo_ended = chatbot_agent(input_text)

        # Step 2: If the conversation is over, reformat it using a second GPT call
        if convo_ended:
            format_prompt = (
                "You are an AI assistant that converts human-readable pizza orders into structured JSON. "
                "Extract the order details from the following response and format them as a JSON object "
                "with the following schema: "
                "{ 'pizzas': [{'quantity': int, 'size': 'small' | 'medium' | 'large', 'crust': 'thin' | 'thick' | 'stuffed'}], "
                "'additional_info': 'any extra comments from the user'}."
                "If no valid order is present, return an empty 'pizzas' list."
                "\n\nUser's message: " + chatbot_response
            )

            messages = [{"role": "system", "content": format_prompt}]
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )

            # Extract JSON response
            formatted_text = response.choices[0].message.content
            try:
                structured_response = json.loads(formatted_text)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON response from GPT")
                raise ValueError("Invalid JSON response received from GPT.")

            return structured_response

        # Step 3: If the conversation is not over, return GPT's natural language response
        return {"response": chatbot_response}

    except Exception as e:
        logger.error("Error processing user input: %s", e)
        raise
