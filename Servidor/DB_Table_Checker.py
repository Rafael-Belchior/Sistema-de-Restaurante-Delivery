from mysql.connector.pooling import PooledMySQLConnection

__conn: PooledMySQLConnection = None  # Guarda a ligação activa para ser reutilizada pelos verificadores

def connect_checker(conn: PooledMySQLConnection):
    # Armazena a ligação recebida para que as restantes funções possam consultar a base de dados
    global __conn
    __conn = conn

def check_username(username: str):
    # Confirma se já existe uma conta com o nome dado e devolve True quando o nome está livre
    global __conn
    cursor = __conn.cursor()
    cursor.execute("SELECT username FROM contas WHERE username = %s", (username,))
    result: str = cursor.fetchone()
    cursor.close()
    return not result

def check_permission(username: str):
    # Recolhe o cargo associado a um determinado utilizador
    global __conn
    cursor = __conn.cursor()
    cursor.execute("SELECT cargo_id FROM contas WHERE username = %s", (username,))
    result: int = cursor.fetchone()
    cursor.close()
    return result

def check_stock(stock_id: int):
    # Verifica o stock actual para um determinado item
    global __conn
    cursor = __conn.cursor()
    cursor.execute("SELECT stock FROM stock WHERE id = %s", (stock_id,))
    result: int = cursor.fetchone()
    cursor.close()
    return result

def check_food(name: str):
    # Garante que não existem dois registos com o mesmo nome no stock
    global __conn
    cursor = __conn.cursor()
    cursor.execute("SELECT nome FROM stock WHERE nome = %s", (name,))
    result: str = cursor.fetchone()
    cursor.close()
    return not result