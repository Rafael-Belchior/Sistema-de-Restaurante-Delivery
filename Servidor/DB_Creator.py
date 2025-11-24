import mysql.connector

def create_database():
    conn = mysql.connector.connect(
        host='192.168.2.51',
        user='proj',
        password='proj',
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS restaurante")
    print("Database created successfully")
    conn.close()