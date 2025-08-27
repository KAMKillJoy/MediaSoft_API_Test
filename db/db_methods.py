import warnings
import allure

from db.postgres_client import PostgresClient


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

    @allure.step("Получение продукта из БД по артикулу: {article}")
    def get_product_by_article(self, article):
        return self.fetch_all("SELECT * FROM product WHERE article = %s", (article,))

    def delete_ent(self, ent: dict):
        table = ent.get('table')
        attribute = ent.get('attribute')
        value = ent.get('value')

        if not table or not attribute or not value:
            raise ValueError("Invalid data for delete_ent: missing table, attribute, or value")

        with allure.step(f"Удаление сущности из таблицы '{table}' по атрибуту '{attribute}' со значением '{value}'"):
            query = f"DELETE FROM {table} WHERE {attribute} = %s"
            self.execute_query(query, (value,))

