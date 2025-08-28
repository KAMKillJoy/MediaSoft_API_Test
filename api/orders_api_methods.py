import allure
from requests import Response
from api.api_client import ApiClient


class OrdersMethods(ApiClient):
    def __init__(self, api_url: str, orders_endpoint: str) -> None:
        super().__init__(api_url)
        self.orders_endpoint = orders_endpoint

    @allure.step("Создание заказа с данными: {data}")
    def create_order(self,customer_id, data: dict) -> Response:
        headers = {"customer_id": customer_id}
        response = self.post(self.orders_endpoint, json=data, headers=headers)
        return response

    @allure.step("Получение заказа с id: {order_id}")
    def get_order(self, customer_id, order_id) -> Response:
        headers = {"customer_id": customer_id}
        response = self.get(self.orders_endpoint + order_id, headers=headers)
        return response

    @allure.step("Удаление заказа с id: {order_id}")
    def delete_order(self, customer_id, order_id) -> Response:
        headers = {"customer_id": customer_id}
        response = self.delete(self.orders_endpoint + order_id, headers=headers)
        return response

    @allure.step("Обновление заказа с id: {order_id}")
    def patch_order(self, customer_id, order_id, data: dict) -> Response:
        headers = {"customer_id": customer_id}
        response = self.patch(self.orders_endpoint + order_id, json=data, headers=headers)
        return response