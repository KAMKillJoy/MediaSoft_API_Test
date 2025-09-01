from typing import Type

from pydantic import ValidationError, BaseModel


class IntestDataCleaner:
    def __bool__(self):
        return True

    def __init__(self):
        self._data = []

    def add(self, table: str, attribute: str, value):
        self._data.append({
            "table": table,
            "attribute": attribute,
            "value": value
        })

    def cleanup(self, db_methods):
        for entry in reversed(self._data):
            db_methods.delete_ent(entry)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"IntestDataCleaner({self._data})"


def validate_response_json(response, model: Type[BaseModel]) -> bool:
    try:
        model.model_validate(response.json())
        return True
    except ValidationError as e:
        raise AssertionError(f"Response data does not match the expected schema: {e}")
