import os
import json
from enum import Enum
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, PositiveInt
import openai

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

class SizeEnum(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"

class CrustEnum(str, Enum):
    thin = "thin"
    thick = "thick"
    stuffed = "stuffed"

class Pizza(BaseModel):
    quantity: PositiveInt
    size: SizeEnum
    crust: CrustEnum

class PizzaRequest(BaseModel):
    pizzas: List[Pizza]

class PizzaResponse(BaseModel):
    pizzas: List[Pizza]
    additional_info: Optional[str] = None

@app.post("/pizzas", response_model=PizzaResponse)
async def process_pizzas(pizza_request: PizzaRequest):
    try:
        system_prompt = (
            "You are a pizza order processing assistant. Your job is to validate and sanitize the following input JSON "
            "containing a 'pizzas' field which is a list of pizza orders. Each pizza order must have a positive integer 'quantity', "
            "a 'size' (small, medium, large), and a 'crust' (thin, thick, stuffed). Discard any invalid orders. If there is extra or "
            "garbage information, include a summary of it in the 'additional_info' field. Return only a valid JSON object with "
            "the keys 'pizzas' and 'additional_info'."
        )

        user_prompt = f"Input data: {pizza_request.model_dump_json()}"

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        response_text = completion["choices"][0]["message"]["content"]

        try:
            parsed_response = json.loads(response_text)
        except Exception as parse_error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse ChatGPT response into JSON: {parse_error}"
            )

        try:
            pizza_response = PizzaResponse(**parsed_response)
        except Exception as validation_error:
            raise HTTPException(
                status_code=500,
                detail=f"Parsed data did not match expected schema: {validation_error}"
            )

        return pizza_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
