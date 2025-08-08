# Kode ini dari panduan brick-by-brick kita sebelumnya
import sqlite3
import os

class SQLiteManager:
    def __init__(self, db_path='data/termux_bdi.db'):
        # Pastikan folder 'data' ada
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        print(f"Database terhubung di: {db_path}")

    def execute_schema(self, schema_query):
        self.cursor.executescript(schema_query)
        self.connection.commit()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.rowcount

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
        
    def fetch_scalar(self, query, params=()):
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.connection.close()
