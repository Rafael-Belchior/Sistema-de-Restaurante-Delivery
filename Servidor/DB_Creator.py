import mysql.connector

def create_database():
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS restaurante")
    print("Database created successfully")
    conn.close()
