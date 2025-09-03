from typing import List, Dict, Any

import psycopg2


class PostgresClient:
    def __init__(self, host: str, dbname: str, user: str, password: str):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None
        self.cursor = None

    def connect(self):
        """Создаём подключение к базе данных"""
        self.conn = psycopg2.connect(
            host=self.host,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
        self.cursor = self.conn.cursor()

    def close(self):
        """Закрываем соединение с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> None:
        """Выполняем запрос без возврата результата (INSERT, UPDATE, DELETE)"""
        try:
            self.cursor.execute(query, params)
            self.conn.commit()  # Обязательное подтверждение транзакции
        except Exception as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()  # Откат транзакции при ошибке

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Выполняем запрос SELECT и возвращаем все строки"""
        self.cursor.execute(query, params)
        columns = [desc[0] for desc in self.cursor.description]  # Получаем имена колонок
        rows = self.cursor.fetchall()

        # Преобразуем в список словарей
        sresult = [dict(zip(columns, row)) for row in rows]
        return sresult

    def fetch_one(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        """Выполняем запрос SELECT и возвращаем одну строку"""
        self.cursor.execute(query, params)
        columns = [desc[0] for desc in self.cursor.description]
        row = self.cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return {}
