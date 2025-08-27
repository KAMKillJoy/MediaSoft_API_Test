@echo off
chcp 65001 > nul

if exist ".\allure-results" (
    allure serve .\allure-results
) else (
    echo Allure отчёт не найден
	pause
)