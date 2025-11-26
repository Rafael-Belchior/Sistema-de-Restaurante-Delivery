from typing import Optional, Tuple

from DB_Connector import *
from DB_Table_Creator import *
from DB_Table_Checker import *
from DB_Table_Editor import *

# Estabelece a ligação à base de dados logo ao arrancar o módulo
conn = connect_to_db()
create_tables(conn)
connect_editor(conn)
connect_checker(conn)


def _ensure_base_roles() -> None:
    """Garante que existem cargos mínimos para o fluxo de autenticação."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cargos (id, nome) VALUES (1, 'Administrador')
        ON DUPLICATE KEY UPDATE nome = VALUES(nome)
    """)
    cursor.execute("""
        INSERT INTO cargos (id, nome) VALUES (2, 'Operador')
        ON DUPLICATE KEY UPDATE nome = VALUES(nome)
    """)
    conn.commit()
    cursor.close()


def _ensure_admin_account() -> None:
    """Cria uma conta de administrador por defeito caso ainda não exista."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM contas WHERE username = %s", ("admin",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO contas (username, password, cargo_id) VALUES (%s, %s, %s)",
            ("admin", "admin", 1),
        )
        conn.commit()
    cursor.close()


def bootstrap_defaults() -> None:
    # Função utilitária chamada pelo servidor para garantir dados essenciais
    _ensure_base_roles()
    _ensure_admin_account()


def _get_role_id(role_name: str) -> Optional[int]:
    # Obtém o id de um cargo específico para poder gravar a conta
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cargos WHERE nome = %s", (role_name,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def _get_role_name(role_id: int) -> Optional[str]:
    # Converte o id do cargo no respectivo nome para enviar ao cliente
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM cargos WHERE id = %s", (role_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def create_account(username: str, password: str, role: str = "Operador") -> Tuple[bool, str]:
    # Regista uma nova conta validando duplicados e atribuindo o cargo pedido
    if not username or not password:
        return False, "Nome e palavra-passe são obrigatórios."

    cursor = conn.cursor()
    if not check_username(username):
        cursor.close()
        return False, "Nome de utilizador já existe."
    role_id = _get_role_id(role)
    if role_id is None:
        cursor.close()
        return False, "Cargo inválido."
    insert_account(username, password)
    edit_account_role(username, role_id)
    cursor.close()
    return True, "Conta criada com sucesso."

def get_account_by_id(user_id: int) -> Optional[dict]:
    # Recolhe os dados essenciais de uma conta a partir do seu ID
    result = get_user(user_id)
    print(f"get_account_by_id({user_id}) result: {result}")
    if not result:
        return None

    _, username, role_id = result
    role_name = _get_role_name(role_id) or "Desconhecido"
    return {"id": user_id, "username": username, "cargo_id": role_id, "cargo_nome": role_name}

def authenticate_account(username: str, password: str) -> Optional[dict]:
    result = check_auth(username, password)
    if not result:
        return None

    user_id, role_id = result
    role_name = _get_role_name(role_id) or "Desconhecido"
    return {"id": user_id, "username": username, "cargo_id": role_id, "cargo_nome": role_name}


def is_admin(user_id: int) -> bool:
    cargo_id = check_permission(user_id)
    return cargo_id == 1  # Assume que o ID 1 é sempre o Administrador

def delete_role(role: int | str) -> None:
    # Elimina um cargo específico da base de dados
    del_role(role)