from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, PositiveInt

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

class ChatInput(BaseModel):
    user_input: str

class PizzaResponse(BaseModel):
    pizzas: List[Pizza]
    additional_info: Optional[str] = None
