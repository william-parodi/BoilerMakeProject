from app.logger import logger
from app.chatbot import chatbot_agent  
import openai
import os
import json

# Initialize OpenAI client with the same API key
api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key=api_key)

async def process_user_input(input_text: str) -> dict:
    """Processes user input through the memory chatbot and formats final orders."""
    try:
        response_text, convo_ended = chatbot_agent(input_text)

        if convo_ended:
            format_prompt = (
                "You are an AI that converts human-readable pizza orders into JSON. "
                "Extract all order details from the response below and structure them as a valid JSON object. "
                "Strictly follow this format:\n\n"
                "{ \"pizzas\": [{\"quantity\": int, \"size\": \"Small\" | \"Medium\" | \"Large\", \"crust\": \"HAND TOSSED\" | \"CRUNCHY THIN CRUST\" | \"NEW YORK STYLE\", \"meat\": \"Pepperoni\" | \"Beef\" | \"Italian Sausage\" | \"Ham\" | \"Philly Steak\" | \"Bacon\" }], "
                "\"additional_info\": \"any extra comments\" }"
                "\n\n### ORDER TEXT ###\n"
                + response_text
                + "\n\n### INSTRUCTIONS ###\n"
                "Return ONLY valid JSON. Do NOT include any explanations, text, markdown, or any additional formatting."
            )


            messages = [{"role": "system", "content": format_prompt}]
            json_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )

            formatted_text = json_response.choices[0].message.content

            try:
                structured_response = json.loads(formatted_text)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON response from GPT")
                raise ValueError("Invalid JSON response received from GPT.")

            return structured_response

        return {"response": response_text}

    except Exception as e:
        logger.error("Error processing user input: %s", e)
        raise
