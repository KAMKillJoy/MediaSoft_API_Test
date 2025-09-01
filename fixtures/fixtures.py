import os

import allure
import pytest
import yaml
from dotenv import load_dotenv

from api.orders_api_methods import OrdersMethods
from api.products_api_methods import ProductsMethods
from db.db_methods import DbMethods
from helpers.helpers import IntestDataCleaner

with open("./config.yaml", "r") as file:
    config = yaml.safe_load(file)


@pytest.fixture(scope="function")
def api_products_methods():
    api = ProductsMethods(config["api"]['base_url'], config["api"]['endpoints']['products'])
    return api


@pytest.fixture(scope="function")
def api_orders_methods():
    api = OrdersMethods(config["api"]['base_url'], config["api"]['endpoints']['orders'])
    return api


dotenv_path = './.env'

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
    cleaner = IntestDataCleaner()
    yield cleaner

    with allure.step("Очищаем тестовые данные"):
        cleaner.cleanup(db_methods)


@pytest.fixture(scope="function")
def create_n_test_products(db_methods, db_intest_data_cleanup):
    created = db_methods.create_random_products(n=50, cleanup=db_intest_data_cleanup, only_available=True)
    return created


@pytest.fixture(scope="function")
def create_n_test_customers(db_methods, db_intest_data_cleanup):
    created = db_methods.create_random_customers(n=50, cleanup=db_intest_data_cleanup, all_active=True)
    return created


@pytest.fixture(scope="function")
def create_test_order(db_methods, db_intest_data_cleanup):
    created = db_methods.create_test_order(cleanup=db_intest_data_cleanup)
    return created
