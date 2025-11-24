from mysql.connector.pooling import PooledMySQLConnection

__conn: PooledMySQLConnection = None

def connect_editor(conn: PooledMySQLConnection):
    __conn = conn

def add_food(cost: float, name: str, stock: int = 0):
    cursor = __conn.cursor()
    cursor.execute("INSERT INTO stock (nome, stock) VALUES (%s, %s)", (name, stock,))
    cursor.execute("SELECT id FROM stock WHERE nome = %s", (name,))
    stock_id = cursor.fetchone()
    cursor.execute("INSERT INTO cardapio (stock_id, valor) VALUES (%s, %s)", (stock_id, cost,))
    cursor.close()

def edit_price(comida: int | str, cost: float):
    cursor = __conn.cursor()
    if (type(comida) == str):
        cursor.execute("SELECT id FROM stock WHERE nome = %s", (comida,))
        comida: int = cursor.fetchone()

    cursor.execute("UPDATE cardapio SET valor = %s WHERE stock_id = %s", (cost, comida,))
    cursor.close()

def remove_food(comida: int | str):
    cursor = __conn.cursor()
    if (type(comida) == str):
        cursor.execute("SELECT id FROM stock WHERE nome = %s", (comida,))
        comida: int = cursor.fetchone()
    
    cursor.execute("DELETE FROM stock WHERE id = %s", (comida,))
    cursor.close()

def insert_account(username: str, password: str):
    cursor = __conn.cursor()
    cursor.execute("INSERT INTO contas (username, password, cargo_id) VALUES (%s, %s, %s)", (username, password, 0))

def edit_account_role(account: int | str, new_role: int):
    cursor = __conn.cursor()
    if (type(account) == str):
        cursor.execute("SELECT id FROM contas WHERE username = %s", (account,))
        account: int = cursor.fetchone()
    cursor.execute("UPDATE contas SET cargo_id = %s WHERE id = %s", (new_role))
    cursor.close()

def del_account(account: int | str):
    cursor = __conn.cursor()
    if (type(account) == str):
        cursor.execute("SELECT id FROM contas WHERE username = %s", (account,))
        account: int = cursor.fetchone()
    cursor.execute("DELETE FROM contas WHERE id = %s", (account,))
    cursor.close()