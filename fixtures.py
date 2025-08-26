import pytest
import yaml

from api.products_methods import ProductsMethods

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

@pytest.fixture(scope="function")
def api_products_methods():
    api = ProductsMethods(config["api"]['base_url'], config["api"]['endpoints']['products'])
    return api