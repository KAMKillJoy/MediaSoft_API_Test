import warnings

import allure

from db.postgres_client import PostgresClient
from factories.product_factory import RequestCreateProductDtoFactory


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
    def create_random_products(self, n: int, cleanup=None) -> list:
        """
        Создаёт n случайных продуктов и сохраняет их в БД.
        Возвращает список созданных продуктов.

        :param n: количество создаваемых продуктов
        :param cleanup: опциональный IntestDataCleaner (или аналог),
                        в который будут добавлены продукты на удаление
        """
        created_products = []

        for _ in range(n):
            product = RequestCreateProductDtoFactory.build()
            product_data = product.model_dump()

            self.insert_product(product_data)
            created_products.append(product_data)

            if cleanup:
                cleanup.add(
                    table="product",
                    attribute="article",
                    value=product_data["article"]
                )

        return created_products

