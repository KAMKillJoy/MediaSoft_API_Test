import uuid
from enum import Enum
from random import choice
from uuid import uuid4

from polyfactory.factories.pydantic_factory import ModelFactory

from schemas.product_schemas import RequestCreateProductDto


class CategoryEnum(str, Enum):
    VEGETABLES = "VEGETABLES"
    FRUITS = "FRUITS"


class RequestCreateProductDtoFactory(ModelFactory):
    __model__ = RequestCreateProductDto

    @classmethod
    def article(cls):
        return str(uuid.uuid4())

    @classmethod
    def category(cls):
        return choice([CategoryEnum.VEGETABLES, CategoryEnum.FRUITS])
