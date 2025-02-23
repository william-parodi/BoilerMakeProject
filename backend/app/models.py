from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, PositiveInt

class SizeEnum(str, Enum):
    small = "Small"
    medium = "Medium"
    large = "Large"

class CrustEnum(str, Enum):
    hand_tossed = "HAND TOSSED"
    crunchy_thin_crust = "CRUNCHY THIN CRUST"
    new_york_style = "NEW YORK STYLE"

class MeatEnum(str, Enum):
    pepperoni = "Pepperoni"
    beef = "Beef"
    italian_sausage = "Italian Sausage"
    ham = "Ham"
    philly_steak = "Philly Steak"
    bacon = "Bacon"

class Pizza(BaseModel):
    quantity: PositiveInt
    size: SizeEnum
    crust: CrustEnum

class ChatInput(BaseModel):
    user_input: str

class PizzaResponse(BaseModel):
    pizzas: List[Pizza]
    additional_info: Optional[str] = None