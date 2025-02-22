from app.logger import logger
from app.chatbot import chatbot_agent  # Importing your chatbot function

async def process_user_input(input_text: str) -> dict:
    """
    Calls your memory-enabled chatbot instead of OpenAI's API.
    """
    try:
        # Call your chatbot function
        response_text = chatbot_agent(input_text)

        # Return a structured response
        return {"response": response_text}

    except Exception as e:
        logger.error("Error processing user input: %s", e)
        raise
