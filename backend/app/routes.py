from fastapi import APIRouter, HTTPException
from app.models import ChatInput, PizzaResponse
from app.services import call_openai
from app.logger import logger

router = APIRouter()

@router.post("/chat", response_model=PizzaResponse)
async def process_chat(chat_input: ChatInput):
    try:
        # Extract the plain text input from the user.
        user_input = chat_input.user_input
        parsed_response = await call_openai(user_input)
        try:
            response = PizzaResponse(**parsed_response)
            return response
        except Exception as validation_error:
            logger.error("Response validation error: %s", validation_error)
            raise HTTPException(
                status_code=500,
                detail=f"Parsed data did not match expected schema: {validation_error}"
            )
    except Exception as e:
        logger.exception("Unhandled exception in process_chat")
        raise HTTPException(status_code=500, detail=str(e))
