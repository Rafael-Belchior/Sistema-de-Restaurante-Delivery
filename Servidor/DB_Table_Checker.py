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

def check_permission(user_id: int):
    # Recolhe o cargo associado a um determinado utilizador
    global __conn
    cursor = __conn.cursor()
    cursor.execute("SELECT cargo_id FROM contas WHERE id = %s", (user_id,))
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

def get_user(user: str | int):
    # Recolhe os dados essenciais de uma conta a partir do seu ID ou nome de utilizador
    global __conn
    cursor = __conn.cursor()
    if (type(user) == str):
        cursor.execute("SELECT id, username, cargo_id FROM contas WHERE username = %s", (user,))
    else:
        cursor.execute("SELECT id, username, cargo_id FROM contas WHERE id = %s", (user,))
    result = cursor.fetchone()
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

def check_auth(username: str, password: str):
    # Valida as credenciais fornecidas e devolve True se forem correctas
    global __conn
    cursor = __conn.cursor()
    cursor.execute(
        "SELECT id, cargo_id FROM contas WHERE username = %s AND password = %s",
        (username, password),
    )
    result: int = cursor.fetchone()
    cursor.close()
    return result

def get_all_roles() -> list[dict]:
    # Recolhe todos os cargos existentes na base de dados
    cursor = __conn.cursor()
    cursor.execute("SELECT id, nome FROM cargos")
    results = cursor.fetchall()
    cursor.close()
    return [{"id": role_id, "nome": nome} for role_id, nome in results]