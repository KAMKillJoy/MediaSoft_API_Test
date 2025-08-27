from decimal import Decimal

import allure

from factories.product_factory import RequestCreateProductDtoFactory
from helpers.helpers import validate_response_json
from schemas.product_schemas import ResponseProductDto


class TestProducts:
    @allure.title("Создание нового продукта")
    @allure.description("Проверка успешного создания продукта через API и его наличия в БД")
    def test_create_product(self, db_intest_data_cleanup, api_products_methods, db_methods):
        with allure.step("Генерация данных для запроса"):
            data = RequestCreateProductDtoFactory.build().model_dump()
            db_intest_data_cleanup.add(table="product", attribute="article", value=data["article"])

        with allure.step("Отправка запроса на создание продукта"):
            response = api_products_methods.create_product(data)
            assert response.status_code == 201, f"Ожидался статус 201, но получен {response.status_code}"

        with allure.step("Валидация схемы ответа"):
            assert validate_response_json(response,
                                          ResponseProductDto), "Ответ не соответствует схеме ResponseProductDto"

        with allure.step("Проверка наличия продукта в БД"):
            assert db_methods.check_product_exists_by_article(
                data['article']), f"Продукт с артикулом {data['article']} не найден в БД"

        response_data = response.json()

        with allure.step("Проверка полей в ответе API"):
            assert response_data['name'] == data[
                'name'], f"Поле name: ожидалось {data['name']}, получено {response_data['name']}"
            assert response_data['article'] == str(
                data['article']), f"Поле article: ожидалось {data['article']}, получено {response_data['article']}"
            assert response_data['category'] == data[
                'category'], f"Поле category: ожидалось {data['category']}, получено {response_data['category']}"
            assert response_data['price'] == data[
                'price'], f"Поле price: ожидалось {data['price']}, получено {response_data['price']}"
            assert response_data['qty'] == data[
                'qty'], f"Поле qty: ожидалось {data['qty']}, получено {response_data['qty']}"

        with allure.step("Проверка данных продукта в БД"):
            db_product = db_methods.get_product_by_article(data['article'])
            assert len(db_product) == 1, f"Ожидался 1 продукт в БД, но найдено: {len(db_product)}"

            db_row = db_product[0]
            assert db_row['name'] == data[
                'name'], f"Поле name в БД: ожидалось {data['name']}, получено {db_row['name']}"
            assert db_row['category'] == data[
                'category'], f"Поле category в БД: ожидалось {data['category']}, получено {db_row['category']}"
            assert db_row['price'] == Decimal(data['price']).quantize(Decimal('0.01')), (
                f"Поле price в БД: ожидалось {Decimal(data['price']).quantize(Decimal('0.01'))}, получено {db_row['price']}"
            )
            assert db_row['qty'] == data['qty'], f"Поле qty в БД: ожидалось {data['qty']}, получено {db_row['qty']}"
