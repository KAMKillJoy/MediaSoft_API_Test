import warnings
from typing import List

import allure
from faker import Faker

from db.postgres_client import PostgresClient
from factories.factories import RequestCreateProductDtoFactory

fake = Faker()


class DbMethods(PostgresClient):
    @allure.step("Проверка существования продукта с артикулом: {article}")
    def check_product_exists_by_article(self, article):
        db_response = self.get_product_by_article(article)
        if len(db_response) == 0:
            return False
        elif len(db_response) == 1:
            return True
        else:
            warnings.warn("В таблице больше одной сущности с таким UUID. Так быть не должно", category=UserWarning)
            return True

    @allure.step("Проверка существования продукта с id: {bdid}")
    def check_product_exists_by_id(self, bdid):
        db_response = self.get_product_by_id(bdid)
        if len(db_response) == 0:
            return False
        elif len(db_response) == 1:
            return True
        else:
            warnings.warn("В таблице больше одной сущности с таким UUID. Так быть не должно", category=UserWarning)
            return True

    @allure.step("Получение продукта из БД по артикулу: {article}")
    def get_product_by_article(self, article):
        return self.fetch_all("SELECT * FROM product WHERE article = %s", (article,))

    def get_product_by_id(self, dbid):
        return self.fetch_all("SELECT * FROM product WHERE id = %s", (dbid,))

    def delete_ent(self, ent: dict):
        table = ent.get('table')
        attribute = ent.get('attribute')
        value = ent.get('value')

        if not table or not attribute or not value:
            raise ValueError("Invalid data for delete_ent: missing table, attribute, or value")

        with allure.step(f"Удаление сущности из таблицы '{table}' по атрибуту '{attribute}' со значением '{value}'"):
            query = f"DELETE FROM {table} WHERE {attribute} = %s"
            self.execute_query(query, (value,))

    @allure.step("Получение всех продуктов из DB")
    def get_all_products_from_db(self) -> list:
        return self.fetch_all("SELECT * FROM product")

    @allure.step("Добавление сущности в таблицу '{table}'")
    def insert_entity(self, table: str, data: dict):
        """
        Универсальный метод вставки записи в указанную таблицу.
        :param table: имя таблицы
        :param data: словарь {имя_колонки: значение}
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, values)

    @allure.step("Добавление продукта в таблицу product: {product_data}")
    def insert_product(self, product_data: dict):
        """
        Добавляет продукт в таблицу product.
        :param product_data: словарь с ключами:
            name, article, dictionary, category, price, qty, is_available (необязательно)
        """
        allowed_fields = {
            "name", "article", "dictionary", "category",
            "price", "qty", "is_available"
        }
        clean_data = {k: v for k, v in product_data.items() if k in allowed_fields}
        self.insert_entity("product", clean_data)

    @allure.step("Создание {n} случайных продуктов в таблице product")
    def create_random_products(
            self,
            n: int,
            cleanup=None,
            only_available: bool = False
    ) -> List[dict]:
        """
        Создаёт n случайных продуктов и сохраняет их в БД.
        Возвращает список словарей с данными продуктов.

        :param n: количество создаваемых продуктов
        :param cleanup: опциональный очиститель (для удаления тестовых данных);
                        в который будут добавлены продукты на удаление
        :param only_available: если True — все продукты создаются как доступные (is_available=True);
                               если False — доступность задаётся случайным булевым значением.
        :return: список словарей с данными продуктов, включая поле is_available (bool)
        """
        created_products = []

        for _ in range(n):
            product = RequestCreateProductDtoFactory.build()
            product_data = product.model_dump()

            if only_available:
                product_data["is_available"] = True
            else:
                product_data["is_available"] = fake.pybool()

            self.insert_product(product_data)
            created_products.append(product_data)

            if cleanup:
                cleanup.add(
                    table="product",
                    attribute="article",
                    value=product_data["article"]
                )

        return created_products

    @allure.step("Добавление клиента: {user_data}")
    def insert_customer(self, user_data: dict) -> None:
        """
        Добавляет клиента в таблицу customer.
        Ключи: login, email, is_active (bool)
        """
        allowed_fields = {"login", "email", "is_active"}
        clean_data = {k: v for k, v in user_data.items() if k in allowed_fields}
        self.insert_entity("customer", clean_data)

    @allure.step("Создание {n} случайных клиентов")
    def create_random_customers(self, n: int, cleanup=None, all_active: bool = False) -> List[dict]:
        """
        Создаёт n случайных клиентов и сохраняет их в БД.

        :param n: количество создаваемых клиентов.
        :param cleanup: опциональный очиститель (для удаления тестовых данных); очищаем по 'login'.
        :param all_active: если True, все клиенты помечаются как активные (is_active=True);
                           если False, 'is_active' задаётся случайным булевым значением.
        :return: список словарей с данными клиентов (ключи: login, email, is_active).
        """
        created = []
        for _ in range(n):
            login = fake.user_name()[-20:]
            email = fake.email()[-20:]
            user_data = {
                "login": login,
                "email": email,
            }
            if all_active:
                user_data["is_active"] = True
            else:
                user_data["is_active"] = fake.boolean()

            self.insert_customer(user_data)
            created.append(user_data)

            if cleanup:
                cleanup.add(table="customer", attribute="login", value=user_data["login"])
        return created

    @allure.step("Получение клиента по login/email: {login}, {email}")
    def get_customer_by_loginnemail(self, login, email):
        sql = """
        SELECT *
        FROM customer
        WHERE login = %s AND email = %s
        LIMIT 1
        """
        params = (login, email)

        return self.fetch_all(sql, params)

    @allure.step("Получение заказа по customer_id: {customer_id} и адресу: {address}")
    def get_order_by_customer_id_n_address(self, customer_id, address):
        sql = """
        SELECT *
        FROM "order"
        WHERE customer_id = %s AND delivery_address = %s
        LIMIT 1
        """
        params = (customer_id, address)

        return self.fetch_all(sql, params)

    @allure.step("Создание заказа для customer_id: {customer_id}")
    def create_order(self, customer_id, delivery_address):
        sql = """
                INSERT INTO "order" (customer_id, status, delivery_address)
                VALUES (%s, %s, %s);
                """
        params = (customer_id, "CREATED", delivery_address)

        self.execute_query(sql, params)

    @allure.step("Создание записи в ordered_product (order_id: {order_id}, product_id: {product_id})")
    def create_ordered_product(self, order_id, product_id, qty, price):
        sql = """
                INSERT INTO "ordered_product" (order_id, product_id, qty, price)
                VALUES (%s, %s, %s, %s);
                """
        params = (order_id, product_id, qty, price)

        self.execute_query(sql, params)

    @allure.step("Получение записи из ordered_product (order_id: {order_id}, product_id: {product_id})")
    def get_ordered_product_by_all_rows(self, order_id, product_id, product_qty, product_price):
        sql = """
                SELECT *
                FROM ordered_product
                WHERE order_id = %s AND product_id = %s AND qty = %s AND price = %s
                LIMIT 1
                """
        params = (order_id, product_id, product_qty, product_price)

        return self.fetch_all(sql, params)

    @allure.step("Создание полного тестового заказа")
    def create_test_order(self, cleanup=None) -> dict:
        """
        Создаёт полный тестовый заказ в базе данных, включая:
        - клиента (customer)
        - продукт (product)
        - заказ (order)
        - заказанный продукт (ordered_product)

        Все сущности создаются с валидными связями между собой,
        что позволяет использовать их для интеграционных тестов.


        :param cleanup: объект IntestDataCleaner (опционально).
                        Если передан — добавляет созданные сущности
                        в него для последующей автоматической очистки.
                        Порядок добавления **обратный** (product → customer → order → ordered_product),
                        так как в методе очистки данные инвертируются для безопасного удаления
                        с учётом внешних ключей.

        :return: словарь с созданными сущностями:
                 {
                    "customer": dict,
                    "product": dict,
                    "order": dict,
                    "ordered_product": dict
                 }
        """

        customer = self.create_random_customers(1, all_active=True)[0]
        customer_from_db = self.get_customer_by_loginnemail(customer["login"], customer["email"])[0]
        customer_id = customer_from_db["id"]

        product = self.create_random_products(1, only_available=True)[0]
        product_from_db = self.get_product_by_article(product["article"])[0]
        product_id = product_from_db["id"]
        product_qty = product_from_db["qty"]
        product_price = product_from_db["price"]

        order_address = fake.address()
        self.create_order(customer_id, order_address)
        order_from_db = self.get_order_by_customer_id_n_address(customer_id, order_address)[0]
        order_id = order_from_db["id"]

        self.create_ordered_product(order_id, product_id, product_qty, product_price)
        ordered_product_from_db = \
            self.get_ordered_product_by_all_rows(order_id, product_id, product_qty, product_price)[0]

        if cleanup:
            '''
            Порядок важен для избегания конфликтов зависимостей в БД!
            В данном случае порядок обратный, так как метод удаления инвертирует итоговый список, 
            что необходимо в общем случае.
            '''
            cleanup.add(table="product", attribute="id", value=product_id)
            cleanup.add(table="customer", attribute="id", value=customer_id)
            cleanup.add(table='\"order\"', attribute="id", value=order_id)
            cleanup.add(table="ordered_product", attribute="order_id", value=order_id)

        return {"customer": customer_from_db,
                "product": product_from_db,
                "order": order_from_db,
                "ordered_product": ordered_product_from_db}
