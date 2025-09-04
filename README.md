# MediaSoft_API_Test
[![Allure Report](https://img.shields.io/badge/Allure%20Report-Open-orange?style=for-the-badge&logo=allure)](https://kamkilljoy.github.io/MediaSoft_API_Test/)

## Тестовое задание AQA
Проект автотестов API сервиса для управления товарами и заказами

## Логины и пароли
#### База данных:
User: postgres_user

Password: postgres_password

## Установка и запуск
- Скачать проект
- Установить python 3 
- Установить зависимости из requirements.txt
- Установить Allure CLI
- создать в корне проекта .env файл с данными из пункта "Логины и пароли": 

`DB_USER=postgres_user
DB_PASSWORD=postgres_password`
- установить Docker
- собрать и запустить контейнер с помощью docker-compose.yml в корне проекта (НЕ docker-compose.ci.yml)
- Запустить run_tests.bat
- Запустить serve_allure.bat чтобы посмотреть предыдущий отчёт
