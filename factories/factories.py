import uuid
from enum import Enum
from random import choice

from polyfactory.factories.pydantic_factory import ModelFactory

from schemas.order_schemas import RequestCreateOrderDto
from schemas.product_schemas import RequestCreateProductDto


class CategoryEnum(str, Enum):
    VEGETABLES = "VEGETABLES"
    FRUITS = "FRUITS"


class RequestCreateProductDtoFactory(ModelFactory):
    __check_model__ = False
    __model__ = RequestCreateProductDto

    @classmethod
    def article(cls):
        return str(uuid.uuid4())

    @classmethod
    def category(cls):
        return choice([CategoryEnum.VEGETABLES, CategoryEnum.FRUITS])


class RequestCreateOrderDtoFactory(ModelFactory):
    __check_model__ = False
    __model__ = RequestCreateOrderDto
