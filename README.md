# MediaSoft_API_Test

Камский Станислав

## Тестовое задание AQA
Проект автотестов API сервиса для управления товарами и заказами

## Логины и пароли
#### База данных:
User: postgres_user
Password: postgres_password

## Установка и запуск
### Локально:
- Скачать проект
- Установить python 3 
- Установить зависимости из requirements.txt
- Установить Allure CLI
- создать в корне проекта .env файл с данными из пункта "Логины и пароли"
- установить Docker
- собрать и запустить контейнер с помощью docker-compose.yml в корне проекта (НЕ docker-compose.ci.yml)
- Запустить run_tests.bat
- Запустить serve_allure.bat чтобы посмотреть предыдущий отчёт

### GitHub Actions:

[![Run Tests](https://img.shields.io/badge/Run%20Tests-Trigger%20CI-blue?style=for-the-badge&logo=githubactions)](https://github.com/KAMKillJoy/MediaSoft_API_Test/actions/workflows/tests.yml)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-Open-orange?style=for-the-badge&logo=allure)](https://kamkilljoy.github.io/MediaSoft_API_Test/)