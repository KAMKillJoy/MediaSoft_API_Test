from typing import Type

from pydantic import ValidationError, BaseModel


def add_data_to_cleanup(intest_data, table: str, attribute: str, value):
    intest_data.append({
        "table": table,
        "attribute": attribute,
        "value": value
    })

def validate_response_json(response, model: Type[BaseModel]) -> bool:
    try:
        model.model_validate(response.json())
        return True
    except ValidationError as e:
        raise AssertionError(f"Response data does not match the expected schema: {e}")