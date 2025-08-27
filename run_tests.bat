@echo off
chcp 65001 > nul
cd "%~dp0"
call .\.venv\Scripts\activate.bat
pytest --alluredir=allure-results
allure serve allure-results