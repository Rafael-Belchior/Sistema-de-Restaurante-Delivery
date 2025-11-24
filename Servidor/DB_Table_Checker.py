from mysql.connector.pooling import PooledMySQLConnection

__conn: PooledMySQLConnection = None

def connect_checker(conn: PooledMySQLConnection):
    __conn = conn

def check_username(username: str):
    cursor = __conn.cursor()
    cursor.execute("SELECT username FROM contas WHERE username = %s", (username,))
    result: str = cursor.fetchone()
    cursor.close()
    return not result

def check_permission(username: str):
    cursor = __conn.cursor()
    cursor.execute("SELECT cargo_id FROM contas WHERE username = %s", (username,))
    result: int = cursor.fetchone()
    cursor.close()
    return result

def check_stock(stock_id: int):
    cursor = __conn.cursor()
    cursor.execute("SELECT stock FROM stock WHERE id = %s", (stock_id,))
    result: int = cursor.fetchone()
    cursor.close()
    return result

def check_food(name: str):
    cursor = __conn.cursor()
    cursor.execute("SELECT nome FROM stock WHERE id = %s", (name,))
    result: str = cursor.fetchone()
    cursor.close()
    return not result