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
        print("Database doesn't exist. Creating database...")
        DB_Creator.create_database()
        return connect_to_db()
    return conn

connect_to_db()