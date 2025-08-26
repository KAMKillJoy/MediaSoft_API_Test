from pydantic import BaseModel, Field, constr, RootModel
from uuid import UUID
from typing import Annotated, List, Optional
from datetime import datetime
from enum import Enum

class RequestCreateProductDto(BaseModel):
    name: Annotated[
        str,
        Field(min_length=4, max_length=20, pattern=r'^[a-zA-Z0-9\sа-яА-ЯёЁ]*$')
    ]
    article: str  # по свагеру string($uuid)
    category: Annotated[
        str,
        Field(min_length=4, max_length=20, pattern=r'^[a-zA-Z0-9]*$')
    ]
    dictionary: Annotated[
        str,
        Field(min_length=4, max_length=500, pattern=r'^[a-zA-Z0-9\sа-яА-ЯёЁ]*$')
    ]
    price: Annotated[float, Field(ge=1)]
    qty: Annotated[int, Field(ge=1)]



class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    CNY = "CNY"
    RUB = "RUB"

class ResponseProductDto(BaseModel):
    name: str
    article: UUID
    id: UUID
    category: str
    price: float
    qty: int
    insertedAt: datetime
    last_qty_changed: datetime
    currency: Currency

class ResponseProductsDto(RootModel[List[ResponseProductDto]]):
    pass


class RequestUpdateProductDto(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=4,
        max_length=20,
        pattern=r'^[a-zA-Z0-9\sа-яА-ЯёЁ]*$'
    )
    id: Optional[UUID]
    article: Optional[UUID]
    category: Optional[str] = Field(
        None,
        pattern=r'^[A-Z_]*$'
    )
    dictionary: Optional[str] = Field(
        None,
        min_length=4,
        max_length=200,
        pattern=r'^[a-zA-Z0-9\sа-яА-ЯёЁ]*$'
    )
    price: Optional[float] = Field(
        None,
        ge=0
    )
    qty: Optional[int] = Field(
        None,
        ge=0
    )