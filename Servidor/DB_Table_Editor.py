from mysql.connector.pooling import PooledMySQLConnection

__conn: PooledMySQLConnection = None  # Referência partilhada da ligação à base de dados

def connect_editor(conn: PooledMySQLConnection):
    # Mantém a ligação para poder executar comandos de escrita na base de dados
    global __conn
    __conn = conn

def add_food(cost: float, name: str, stock: int = 0):
    # Adiciona um item ao cardápio e sincroniza o stock inicial
    cursor = __conn.cursor()
    cursor.execute("INSERT INTO stock (nome, stock) VALUES (%s, %s)", (name, stock,))
    cursor.execute("SELECT id FROM stock WHERE nome = %s", (name,))
    stock_id = cursor.fetchone()
    stock_id = stock_id[0] if stock_id else None
    cursor.execute("INSERT INTO cardapio (stock_id, valor) VALUES (%s, %s)", (stock_id, cost,))
    __conn.commit()
    cursor.close()

def edit_price(comida: int | str, cost: float):
    # Actualiza o preço de um item identificado por id ou nome
    cursor = __conn.cursor()
    if (type(comida) == str):
        cursor.execute("SELECT id FROM stock WHERE nome = %s", (comida,))
        comida_tuple = cursor.fetchone()
        comida = comida_tuple[0] if comida_tuple else None

    cursor.execute("UPDATE cardapio SET valor = %s WHERE stock_id = %s", (cost, comida,))
    __conn.commit()
    cursor.close()

def remove_food(comida: int | str):
    # Remove um item do stock e respectivos registos associados
    cursor = __conn.cursor()
    if (type(comida) == str):
        cursor.execute("SELECT id FROM stock WHERE nome = %s", (comida,))
        comida_tuple = cursor.fetchone()
        comida = comida_tuple[0] if comida_tuple else None
    
    cursor.execute("DELETE FROM stock WHERE id = %s", (comida,))
    __conn.commit()
    cursor.close()

def insert_account(username: str, password: str):
    # Cria uma conta base com cargo zero (será ajustado mais tarde)
    cursor = __conn.cursor()
    cursor.execute("INSERT INTO contas (username, password, cargo_id) VALUES (%s, %s, %s)", (username, password, 0))
    __conn.commit()

def edit_account_role(account: int | str, new_role: int):
    # Actualiza o cargo associado a uma conta existente
    cursor = __conn.cursor()
    if (type(account) == str):
        cursor.execute("SELECT id FROM contas WHERE username = %s", (account,))
        account_tuple = cursor.fetchone()
        account = account_tuple[0] if account_tuple else None
    cursor.execute("UPDATE contas SET cargo_id = %s WHERE id = %s", (new_role, account))
    __conn.commit()
    cursor.close()

def del_account(account: int | str):
    # Elimina uma conta pelo id ou username
    cursor = __conn.cursor()
    if (type(account) == str):
        cursor.execute("SELECT id FROM contas WHERE username = %s", (account,))
        account_tuple = cursor.fetchone()
        account = account_tuple[0] if account_tuple else None
    cursor.execute("DELETE FROM contas WHERE id = %s", (account,))
    __conn.commit()
    cursor.close()

def del_role(role: int | str):
    # Elimina um cargo pelo id ou nome
    cursor = __conn.cursor()
    if (type(role) == str):
        cursor.execute("SELECT id FROM cargos WHERE nome = %s", (role,))
        role_tuple = cursor.fetchone()
        role = role_tuple[0] if role_tuple else None
    cursor.execute("DELETE FROM cargos WHERE id = %s", (role,))
    __conn.commit()
    cursor.close()