from mysql.connector.pooling import PooledMySQLConnection

__conn: PooledMySQLConnection = None

def connect_editor(conn: PooledMySQLConnection):
    __conn = conn