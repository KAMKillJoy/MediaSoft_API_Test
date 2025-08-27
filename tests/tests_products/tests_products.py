import random
from decimal import Decimal

import allure

from factories.product_factory import RequestCreateProductDtoFactory
from helpers.helpers import validate_response_json
from schemas.product_schemas import ResponseProductDto, ResponseProductsDto, RequestUpdateProductDto


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

            expected_price = Decimal(data['price']).quantize(Decimal('0.01'))
            actual_price = db_row['price']
            assert actual_price == expected_price, (
                f"Поле price в БД: ожидалось {expected_price}, получено {actual_price}"
            )
            assert db_row['qty'] == data['qty'], f"Поле qty в БД: ожидалось {data['qty']}, получено {db_row['qty']}"

    def test_get_all_products(self, db_intest_data_cleanup, api_products_methods, db_methods, create_n_test_products):
        with allure.step("Отправка запроса всех продуктов"):
            response = api_products_methods.get_products()

            assert response.status_code == 200, f"Ожидался статус 200, но получен {response.status_code}"

        with allure.step("Валидация схемы ответа"):
            assert validate_response_json(response,
                                          ResponseProductsDto), "Ответ не соответствует схеме ResponseProductsDto"

        with allure.step("Проверка соответствия ответа апи содержимому БД"):
            api_products = response.json()
            db_products = db_methods.get_all_products_from_db()
            db_products_count = len(db_products)
            resp_products_count = len(api_products)
            with allure.step("Проверка соответствия количества продуктов в ответе API и в БД"):
                assert resp_products_count == db_products_count, (
                    f"Количество продуктов в ответе API {resp_products_count},"
                    f"в БД {db_products_count}. Должно быть равно!")

        db_index = {p['article']: p for p in db_products}
        for api_product in api_products:
            article = api_product['article']
            assert article in db_index, f"Продукт с артикулом {article} есть в API, но нет в БД"
            db_product = db_index[article]

            assert api_product['name'] == db_product['name'], f"[{article}] Несовпадение name"
            assert api_product['category'] == db_product['category'], f"[{article}] Несовпадение category"
            assert Decimal(api_product['price']).quantize(Decimal('0.01')) == db_product[
                'price'], f"[{article}] Несовпадение price"
            assert api_product['qty'] == db_product['qty'], f"[{article}] Несовпадение qty"

    def test_patch_product_qty(
            self,
            db_intest_data_cleanup,
            api_products_methods,
            db_methods,
            create_n_test_products
    ):
        db_products = db_methods.get_all_products_from_db()
        product_for_test = random.choice(db_products)
        product_for_test_id = product_for_test['id']
        old_qty = product_for_test['qty']
        new_qty = random.randint(1, 100)
        new_data = {"id": product_for_test_id, "qty": new_qty}
        old_db_product = db_methods.get_product_by_id(product_for_test_id)[0]

        with allure.step("Отправка запроса на изменение количества продукта"):
            response = api_products_methods.patch_product(new_data)
            resp_data = response.json()

            assert response.status_code == 200, (
                f"Ожидался статус 200, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Валидация схемы ответа"):
            assert validate_response_json(response, RequestUpdateProductDto), (
                "Ответ не соответствует схеме RequestUpdateProductDto. "
                f"Ответ: {response.text}"
            )

        with allure.step(f"Проверка, что в базе данных количество равно {new_qty}"):
            patched_db_product = db_methods.get_product_by_id(product_for_test_id)[0]
            assert patched_db_product['qty'] == new_qty, (
                f"Количество в БД не обновилось. Было: {old_qty}, стало: {patched_db_product['qty']}, ожидалось: {new_qty}"
            )

        with allure.step(f"Проверка, что в ответе API количество равно {new_qty}"):
            assert resp_data['qty'] == new_qty, (
                f"Количество в API-ответе некорректно. Было: {old_qty}, стало: {resp_data['qty']}, ожидалось: {new_qty}"
            )

        with allure.step("Проверка что в базе данных поменялось поле last_qty_changed"):
            assert old_db_product.get("last_qty_changed") != patched_db_product["last_qty_changed"], (
                f"Поле last_qty_changed не изменилось. "
                f"Было: {old_db_product.get('last_qty_changed')}, "
                f"Стало: {patched_db_product.get('last_qty_changed')}"
            )

    def test_get_product_by_id(
            self,
            db_intest_data_cleanup,
            api_products_methods,
            db_methods,
            create_n_test_products
    ):
        db_products = db_methods.get_all_products_from_db()
        product_for_test = random.choice(db_products)
        product_for_test_id = product_for_test['id']

        with allure.step("Отправка запроса на получение продукта по ID"):
            response = api_products_methods.get_product(product_for_test_id)
            resp_data = response.json()

            assert response.status_code == 200, (
                f"Ожидался статус 200, но получен {response.status_code}. "
                f"Ответ: {response.text}"
            )

        with allure.step("Валидация схемы ответа"):
            assert validate_response_json(response,
                                          ResponseProductDto), "Ответ не соответствует схеме ResponseProductDto"

        with allure.step("Проверка полей в ответе API"):
            assert product_for_test['name'] == resp_data[
                'name'], f"Поле name в БД: ожидалось {resp_data['name']}, получено {product_for_test['name']}"
            assert product_for_test['category'] == resp_data[
                'category'], f"Поле category в БД: ожидалось {resp_data['category']}, получено {product_for_test['category']}"

            expected_price = Decimal(resp_data['price']).quantize(Decimal('0.01'))
            actual_price = product_for_test['price']
            assert actual_price == expected_price, f"Поле price в БД: ожидалось {expected_price}, получено {actual_price}"
            assert product_for_test['qty'] == resp_data[
                'qty'], f"Поле qty в БД: ожидалось {resp_data['qty']}, получено {product_for_test['qty']}"
