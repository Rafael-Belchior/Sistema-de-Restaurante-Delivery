from mysql.connector.pooling import PooledMySQLConnection, MySQLConnectionAbstract


def create_tables(conn: PooledMySQLConnection | MySQLConnectionAbstract):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS contas (id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(30) UNIQUE, password VARCHAR(10), cargo_id INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS cargos (id INT PRIMARY KEY AUTO_INCREMENT, nome VARCHAR(100) UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS cardapio (id INT PRIMARY KEY AUTO_INCREMENT, comida_id INT, valor REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS stock (id INT PRIMARY KEY AUTO_INCREMENT, nome VARCHAR(100), stock INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS recibo (fatura_id INT, conta_id INT, data DATETIME)")
    cursor.execute("CREATE TABLE IF NOT EXISTS fatura (id INT, comida_id INT, quantidade INT)")
    conn.commit()