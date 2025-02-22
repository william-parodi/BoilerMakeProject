from openai import AsyncOpenAI
import json
from app.config import settings
from app.logger import logger

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def call_openai(input_text: str) -> dict:
    system_prompt = (
        "You are a pizza order processing assistant. Your job is to validate and sanitize a natural language string "
        "describing a pizza order. Extract the details into a JSON object with a 'pizzas' key (a list of pizza orders) "
        "and an 'additional_info' field for any extra information. Each pizza order should include a positive integer 'quantity', "
        "'size' (small, medium, large), and 'crust' (thin, thick, stuffed). Discard any invalid orders. "
        "Return only a valid JSON object with the keys 'pizzas' and 'additional_info'."
    )
    user_prompt = f"Input: {input_text}"
    
    try:
        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        response_text = completion.choices[0].message.content
        parsed_response = json.loads(response_text)
        return parsed_response
    
    except Exception as e:
        logger.error("Error calling OpenAI API: %s", e)
        raise
