from fastapi import APIRouter, HTTPException
from app.models import PizzaRequest, PizzaResponse
from app.services import call_openai
from app.logger import logger

router = APIRouter()

@router.post("/pizzas", response_model=PizzaResponse)
async def process_pizzas(pizza_request: PizzaRequest):
    try:
        pizza_request_json = pizza_request.model_dump_json()
        parsed_response = await call_openai(pizza_request_json)
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
        logger.exception("Unhandled exception in process_pizzas")
        raise HTTPException(status_code=500, detail=str(e))
