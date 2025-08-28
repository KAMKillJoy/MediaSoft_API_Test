from pydantic import BaseModel, Field, constr, RootModel
from uuid import UUID
from typing import Annotated, List, Optional
from datetime import datetime
from enum import Enum

class ProductSummaryDto(BaseModel):
    id: str
    qty: Annotated[int, Field(ge=1, le=10)]

class RequestCreateOrderDto(BaseModel):
    deliveryAddress: Annotated[
        str,
        Field(min_length=4, max_length=255, pattern=r'^[a-zA-Z0-9\s]*$')
    ]
    products: List[ProductSummaryDto]


class OrderSummaryDto(BaseModel):
    name: str
    id: str
    price: float
    qty: int

class GetOrderDto(BaseModel):
    orderId: str
    products: List[OrderSummaryDto]
    totalPrice: float

class UuidResponse(RootModel[str]):
    pass