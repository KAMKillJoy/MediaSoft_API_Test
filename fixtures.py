import os

import pytest
import yaml
from dotenv import load_dotenv

from api.products_api_methods import ProductsMethods
from db.db_methods import DbMethods

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)


@pytest.fixture(scope="function")
def api_products_methods():
    api = ProductsMethods(config["api"]['base_url'], config["api"]['endpoints']['products'])
    return api


dotenv_path = '.env'

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


@pytest.fixture(scope="session")
def db_methods():
    db = DbMethods(host=config["db"]["db_host"],
                   dbname=config["db"]["db_name"],
                   user=os.getenv("DB_USER"),
                   password=os.getenv("DB_PASSWORD")
                   )
    db.connect()
    yield db
    db.close()

@pytest.fixture(scope="session")
def db_intest_data_cleanup(db_methods):
    intest_data = list()
    yield intest_data

    for i in intest_data:
        db_methods.delete_ent(i)