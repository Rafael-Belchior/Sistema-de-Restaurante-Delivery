import mysql.connector
import DB_Creator

def connect_to_db():
    conn = None
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='restaurante'
        )
    except:
        DB_Creator.create_database()
        return connect_to_db()
    return conn