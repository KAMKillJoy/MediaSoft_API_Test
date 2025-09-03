from typing import Annotated, List

from pydantic import BaseModel, Field, RootModel


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


class CreateOrderResponse(RootModel[str]):
    pass


class RequestUpdateOrderDto(BaseModel):
    products: List[ProductSummaryDto]
