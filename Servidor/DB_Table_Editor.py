from mysql.connector.pooling import PooledMySQLConnection, MySQLConnectionAbstract

__conn = None

def connect_editor(conn: PooledMySQLConnection | MySQLConnectionAbstract):
    __conn = conn