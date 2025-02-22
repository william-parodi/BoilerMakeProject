import json
import openai
from app.config import settings
from app.logger import logger

# Set the API key from configuration
openai.api_key = settings.openai_api_key

async def call_openai(pizza_request_json: str) -> dict:
    system_prompt = (
        "You are a pizza order processing assistant. Your job is to validate and sanitize the following input JSON "
        "containing a 'pizzas' field which is a list of pizza orders. Each pizza order must have a positive integer 'quantity', "
        "a 'size' (small, medium, large), and a 'crust' (thin, thick, stuffed). Discard any invalid orders. If there is extra or "
        "garbage information, include a summary of it in the 'additional_info' field. Return only a valid JSON object with "
        "the keys 'pizzas' and 'additional_info'."
    )
    user_prompt = f"Input data: {pizza_request_json}"
    try:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        response_text = completion["choices"][0]["message"]["content"]
        parsed_response = json.loads(response_text)
        return parsed_response
    except Exception as e:
        logger.error("Error calling OpenAI API: %s", e)
        raise
        