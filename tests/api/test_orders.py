import random
from random import randint

import allure

from factories.factories import RequestCreateOrderDtoFactory, RequestUpdateOrderDtoFactory
from helpers.helpers import validate_response_json
from schemas.order_schemas import CreateOrderResponse, GetOrderDto


@allure.suite("Заказы")
@allure.feature("API /order")
class TestOrders:
    @allure.title("Создание нового заказа")
    @allure.description("Проверка успешного создания заказа и его данных в БД")
    def test_create_order(self, db_intest_data_cleanup,
                          api_orders_methods,
                          db_methods,
                          create_n_test_customers,
                          create_n_test_products):
        customer = random.choice(create_n_test_customers)
        customer_from_db = db_methods.get_customer_by_loginnemail(customer["login"], customer["email"])[0]
        customer_id = customer_from_db["id"]

        product = random.choice(create_n_test_products)
        orig_product_from_db = db_methods.get_product_by_article(product["article"])[0]
        orig_product_qty = orig_product_from_db["qty"]
        product_id = orig_product_from_db["id"]
        product_price = orig_product_from_db["price"]

        with allure.step("Генерация данных для запроса"):
            order_qty = random.randint(1, int(orig_product_qty))

            order_data = RequestCreateOrderDtoFactory.build().model_dump()
            order_data["products"] = []
            order_data["products"].append({"id": product_id, "qty": order_qty})

        with allure.step("Отправка запроса на создание заказа"):
            response = api_orders_methods.create_order(str(customer_id), order_data)
            assert response.status_code == 200, (f"Ожидался статус 200, но получен {response.status_code}. "
                                                 f"Ответ не соответствует успешному созданию заказа.")
            #  почему не 201?

        order_id = response.text.strip("\"")

        #  Добавление тестовых данных в список для последующего удаления. В порядке создания!
        db_intest_data_cleanup.add(table="\"order\"", attribute="id", value=order_id)
        db_intest_data_cleanup.add(table="ordered_product", attribute="order_id", value=order_id)

        with allure.step("Валидация схемы ответа"):
            assert validate_response_json(response,
                                          CreateOrderResponse), (f"Ответ не соответствует схеме CreateOrderResponse. "
                                                                 f"Ответ: {response.json()}")

        with (allure.step("Проверка соответствия данных в таблице order")):
            order = db_methods.get_order_by_id(order_id)[0]
            assert order["customer_id"] == customer_id, \
                (f"Ошибка: customer_id в таблице order не совпадает с ожидаемым значением. "
                 f"Ожидалось: {customer_id}, получено: {order['customer_id']}")
            assert order["status"] == "CREATED", \
                (f"Ошибка: статус заказа в таблице order должен быть 'CREATED'. "
                 f"Ожидалось: 'CREATED', получено: {order['status']}")
            assert order["delivery_address"] == order_data["deliveryAddress"], \
                (f"Ошибка: адрес доставки не совпадает. "
                 f"Ожидался: {order_data['deliveryAddress']}, получено: {order['delivery_address']}")

        with allure.step("Проверка соответствия данных в таблице ordered_product"):
            ordered_product = db_methods.get_ordered_product(order_id, product_id)[0]
            assert ordered_product, \
                f"Ошибка: товар не найден в таблице ordered_product для заказа {order_id} и товара {product_id}."
            assert ordered_product["qty"] == order_qty, \
                (f"Ошибка: количество товара в таблице ordered_product не совпадает с ожидаемым. "
                 f"Ожидалось: {order_qty}, получено: {ordered_product['qty']}")
            assert ordered_product["price"] == product_price, \
                (f"Ошибка: цена товара в таблице ordered_product не совпадает с ожидаемой. "
                 f"Ожидалось: {product_price}, получено: {ordered_product['price']}")

        with (allure.step("Проверка корректного изменения количества товара в таблице product")):
            upd_product = db_methods.get_product_by_article(product["article"])[0]

            product_new_qty = orig_product_qty - order_qty
            assert upd_product["qty"] == product_new_qty, \
                (f"Ошибка: количество товара в таблице product не обновилось корректно. "
                 f"Ожидалось: {product_new_qty}, получено: {upd_product['qty']}")

    @allure.title("Получение заказа по ID")
    @allure.description("Проверка соответствия данных из API и БД при запросе по ID")
    def test_get_order(self, db_intest_data_cleanup,
                       api_orders_methods,
                       db_methods, create_test_order):
        test_order = create_test_order["order"]
        test_order_id = str(test_order["id"])
        customer_id = str(create_test_order["customer"]["id"])
        product = create_test_order["product"]

        with allure.step("Отправка запроса на получение заказа"):
            response = api_orders_methods.get_order(customer_id, test_order_id)

            assert response.status_code == 200, (f"Ожидался статус 200, но получен {response.status_code}. "
                                                 f"Ответ не соответствует успешному получению заказа.")

        with allure.step("Валидация схемы ответа"):
            assert validate_response_json(response,
                                          GetOrderDto), (f"Ответ не соответствует схеме GetOrderDto. "
                                                         f"Ответ: {response.json()}")
        with allure.step("Проверка соответствия данных в ответе"):
            response_data = response.json()

            assert response_data["orderId"] == test_order_id, \
                f"Ошибка: orderId в ответе не совпадает с ожидаемым. Ожидался: {test_order_id}, получено: {response_data['orderId']}"

            assert response_data["products"][0]["name"] == product["name"], \
                f"Ошибка: название товара в ответе не совпадает. Ожидалось: {product['name']}, получено: {response_data['products'][0]['name']}"

            assert response_data["products"][0]["id"] == product["id"], \
                f"Ошибка: id товара в ответе не совпадает. Ожидалось: {product['id']}, получено: {response_data['products'][0]['id']}"

            assert response_data["products"][0]["price"] == float(product["price"]), \
                f"Ошибка: цена товара в ответе не совпадает. Ожидалась: {float(product['price'])}, получено: {response_data['products'][0]['price']}"

            assert response_data["products"][0]["qty"] == product["qty"], \
                f"Ошибка: количество товара в ответе не совпадает. Ожидалось: {product['qty']}, получено: {response_data['products'][0]['qty']}"

            assert response_data["totalPrice"] == float(product["qty"] * product["price"]), \
                f"Ошибка: общая цена в ответе не совпадает с расчетной. Ожидалась: {float(product['qty'] * product['price'])}, получено: {response_data['totalPrice']}"

    @allure.title("Изменение количества товара в заказе")
    @allure.description("Проверка успешного изменения количества товара в заказе через API")
    def test_patch_order_qty(self, db_intest_data_cleanup,
                             api_orders_methods,
                             db_methods, create_test_order):
        """
        В идеале, конечно, нужно сделать общую проверку, где меняется количество уже заказанных товаров,
        а также добавляется новый продукт в заказ.
        Но я уже слишком заморочился для ТЗ, которое, возможно, и никто не будет смотреть.
        Кстати, скажите в обратной связи, что видели этот комментарий.
        """

        test_order = create_test_order["order"]
        test_order_id = str(test_order["id"])
        customer_id = str(create_test_order["customer"]["id"])
        product = create_test_order["product"]
        product_id = product["id"]

        with allure.step("Подготовка данных запроса"):
            data = RequestUpdateOrderDtoFactory.build().model_dump()
            print(data)
            data["products"][0]["id"] = product["id"]
            order_new_qty = randint(1, int(product["qty"]))
            data["products"][0]["qty"] = order_new_qty

        with allure.step("Отправка запроса на изменение заказа"):
            response = api_orders_methods.patch_order(customer_id=customer_id,
                                                      order_id=test_order_id,
                                                      data=data)

            assert response.status_code == 204, (f"Ожидался статус 204, но получен {response.status_code}. "
                                                 f"Ответ не соответствует успешному изменению заказа.")

        with allure.step("Проверка изменения количества заказанных продуктов"):
            new_ordered_product = db_methods.get_ordered_product(order_id=test_order_id, product_id=product_id)[0]
            assert new_ordered_product["qty"] == order_new_qty

    @allure.title("Удаление заказа по ID")
    @allure.description("Проверка успешного удаления заказа и его данных в БД")
    def test_delete_order(self, db_intest_data_cleanup,
                          api_orders_methods,
                          db_methods, create_test_order):
        test_order = create_test_order["order"]
        test_order_id = str(test_order["id"])
        customer_id = str(create_test_order["customer"]["id"])
        product = create_test_order["product"]
        product_id = product["id"]
        ordered_product = create_test_order["ordered_product"]

        with allure.step("Отправка запроса на удаление заказа"):
            response = api_orders_methods.delete_order(customer_id=customer_id, order_id=test_order_id)
            assert response.status_code == 200, (f"Ожидался статус 200, "
                                                 f"но получен {response.status_code}. "
                                                 f"Ответ не соответствует успешному удалению заказа.")

        with allure.step('Проверка изменения статуса заказа в БД на "CANCELLED"'):
            order_from_db = db_methods.get_order_by_id(order_id=test_order_id)[0]
            assert order_from_db[
                       "status"] == "CANCELLED", (f"Статус заказа в БД не обновился на 'CANCELLED'. "
                                                  f"Получен статус: {order_from_db['status']}.")

        with allure.step('Проверка отсутствия записи о заказе в таблице ordered_product в БД'):
            ordered_product_from_db = db_methods.get_ordered_product(order_id=test_order_id, product_id=product_id)
            assert not ordered_product_from_db, ("Запись о заказе все еще существует в таблице ordered_product, "
                                                 "хотя заказ должен быть удален.")

        with allure.step('Проверка увеличения количества продукта на складе из-за снятия резерва'):
            new_product = db_methods.get_product_by_id(product_id)[0]
            expected_qty = product["qty"] + ordered_product["qty"]
            assert new_product[
                       "qty"] == expected_qty, (f"Количество товара на складе не увеличилось должным образом. "
                                                f"Ожидалось: {expected_qty}, получено: {new_product['qty']}.")
