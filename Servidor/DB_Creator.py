import mysql.connector

def create_database():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS restaurante")
    conn.close()