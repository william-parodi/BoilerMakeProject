from fastapi import APIRouter, HTTPException
from app.models import ChatInput
from app.services import process_user_input  # Now calling chatbot_agent
from app.logger import logger

router = APIRouter()

@router.post("/chat")
async def process_chat(chat_input: ChatInput):
    """
    FastAPI route that takes user input and calls your chatbot.
    """
    try:
        user_input = chat_input.user_input
        chatbot_response = await process_user_input(user_input)  # Uses chatbot_agent()

        return chatbot_response

    except Exception as e:
        logger.exception("Unhandled exception in process_chat")
        raise HTTPException(status_code=500, detail=str(e))
