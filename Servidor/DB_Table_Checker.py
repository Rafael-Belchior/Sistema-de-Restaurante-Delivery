from mysql.connector.pooling import PooledMySQLConnection, MySQLConnectionAbstract

__conn: PooledMySQLConnection | MySQLConnectionAbstract = None

def connect_checker(conn: PooledMySQLConnection | MySQLConnectionAbstract):
    __conn = conn

def check_username(username):
    cursor = __conn.cursor()
    cursor.execute("SELECT username FROM contas WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    return not result

def check_permission(username):
    cursor = __conn.cursor()
    cursor.execute("SELECT cargo_id FROM contas WHERE username = %s", (username,))
    result: int = cursor.fetchone()
    cursor.close()
    return result