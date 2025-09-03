import logging

import requests

# Настройка логирования
logger = logging.getLogger("api_client")
logging.basicConfig(level=logging.INFO)


class ApiClient:
    """
    Клиент для взаимодействия с API с использованием библиотеки requests.
    """

    def __init__(self, api_url):
        self.base_url = api_url

    def log_request(self, method: str, url: str, **kwargs):
        """
        Логирование отправляемых запросов.
        """
        logger.info(f"Отправка {method} запроса на {url} с параметрами: {kwargs}")

    def request(self, method: str, endpoint: str, auth=None, **kwargs) -> requests.Response:
        """
        Выполнение HTTP-запроса.
        """
        url = self.base_url + endpoint
        self.log_request(method, url, **kwargs)

        try:
            response = requests.request(method, url, auth=auth, **kwargs)
            response.raise_for_status()  # Проверка на ошибки
            return response
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP ошибка: {err}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    def get(self, endpoint: str, auth=None, **kwargs) -> requests.Response:
        """
        Выполнение GET-запроса.
        """
        return self.request("GET", endpoint, auth, **kwargs)

    def post(self, endpoint: str, auth=None, **kwargs) -> requests.Response:
        """
        Выполнение POST-запроса.
        """
        return self.request("POST", endpoint, auth, **kwargs)

    def put(self, endpoint: str, auth=None, **kwargs) -> requests.Response:
        """
        Выполнение PUT-запроса.
        """
        return self.request("PUT", endpoint, auth, **kwargs)

    def delete(self, endpoint: str, auth=None, **kwargs) -> requests.Response:
        """
        Выполнение DELETE-запроса.
        """
        return self.request("DELETE", endpoint, auth, **kwargs)

    def patch(self, endpoint: str, auth=None, **kwargs) -> requests.Response:
        """
        Выполнение PATCH-запроса.
        """
        return self.request("PATCH", endpoint, auth, **kwargs)
