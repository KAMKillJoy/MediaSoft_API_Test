import allure
from requests import Response
from api.api_client import ApiClient


class ProductsMethods(ApiClient):
    def __init__(self, api_url: str, products_endpoint: str) -> None:
        super().__init__(api_url)
        self.products_endpoint = products_endpoint

    @allure.step("Создание продукта с данными: {data}")
    def create_product(self, data: dict) -> Response:
        response = self.post(self.products_endpoint + "/products", json=data)
        return response

    @allure.step("Получение списка всех продуктов")
    def get_products(self) -> Response:
        response = self.get(self.products_endpoint)
        return response

    @allure.step("Обновление продукта с данными: {data}")
    def patch_product(self, data: dict) -> Response:
        response = self.patch(self.products_endpoint, json=data)
        return response

    @allure.step("Получение продукта по ID: {product_id}")
    def get_product(self, product_id: str) -> Response:
        response = self.get(self.products_endpoint +"/"+ product_id)
        return response

    @allure.step("Удаление продукта по ID: {product_id}")
    def delete_product(self, product_id: str) -> Response:
        response = self.delete(self.products_endpoint + f"/products/{product_id}")
        return response
