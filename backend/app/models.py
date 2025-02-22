from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, PositiveInt

class SizeEnum(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"

class CrustEnum(str, Enum):
    hand_tossed = "hand tossed"
    crunchy_thin_crust = "crunchy thin crust"
    new_york_style = "new york style"

class Pizza(BaseModel):
    quantity: PositiveInt
    size: SizeEnum
    crust: CrustEnum

class ChatInput(BaseModel):
    user_input: str

class PizzaResponse(BaseModel):
    pizzas: List[Pizza]
    additional_info: Optional[str] = None
