from requests import Response

from api.api_client import ApiClient


class ProductsMethods(ApiClient):
    def __init__(self, api_url: str, products_endpoint: str) -> None:
        super().__init__(api_url)
        self.products_endpoint = products_endpoint

    def create_product(self, data: dict) -> Response:
        response = self.post(self.products_endpoint + "/products", json=data)
        return response

    def get_products(self) -> Response:
        response = self.get(self.products_endpoint)
        return response

    def patch_product(self, data: dict) -> Response:
        response = self.patch(self.products_endpoint, json=data)
        return response

    def get_product(self, product_id: str) -> Response:
        response = self.get(self.products_endpoint + f"/products/{product_id}")
        return response

    def delete_product(self, product_id: str) -> Response:
        response = self.delete(self.products_endpoint + f"/products/{product_id}")
        return response
