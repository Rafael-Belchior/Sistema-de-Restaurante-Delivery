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
    result = check_permission(user_id)
    if result is None:
        return False
    cargo_id = result[0] if isinstance(result, tuple) else result
    return cargo_id == 1  # Assume que o ID 1 é sempre o Administrador


def delete_role(role: int | str) -> Tuple[bool, str]:
    # Elimina um cargo específico da base de dados
    try:
        del_role(role)
        return True, "Cargo eliminado com sucesso."
    except Exception as e:
        return False, f"Erro ao eliminar cargo: {e}"


def get_all_accounts() -> list[dict]:
    """Recolhe todas as contas existentes na base de dados."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, cargo_id FROM contas")
    results = cursor.fetchall()
    cursor.close()
    accounts = []
    for user_id, username, cargo_id in results:
        role_name = _get_role_name(cargo_id) or "Desconhecido"
        accounts.append({"id": user_id, "username": username, "cargo_id": cargo_id, "cargo_nome": role_name})
    return accounts


def update_account(user_id: int, new_username: str = None, new_password: str = None, new_role_id: int = None) -> Tuple[bool, str]:
    """Actualiza os dados de uma conta existente."""
    cursor = conn.cursor()
    try:
        if new_username:
            cursor.execute("UPDATE contas SET username = %s WHERE id = %s", (new_username, user_id))
        if new_password:
            cursor.execute("UPDATE contas SET password = %s WHERE id = %s", (new_password, user_id))
        if new_role_id:
            cursor.execute("UPDATE contas SET cargo_id = %s WHERE id = %s", (new_role_id, user_id))
        conn.commit()
        cursor.close()
        return True, "Conta actualizada com sucesso."
    except Exception as e:
        cursor.close()
        return False, f"Erro ao actualizar conta: {e}"


def delete_account(user_id: int) -> Tuple[bool, str]:
    """Elimina uma conta da base de dados."""
    try:
        del_account(user_id)
        return True, "Conta eliminada com sucesso."
    except Exception as e:
        return False, f"Erro ao eliminar conta: {e}"


def create_role(nome: str) -> Tuple[bool, str]:
    """Cria um novo cargo na base de dados."""
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cargos (nome) VALUES (%s)", (nome,))
        conn.commit()
        cursor.close()
        return True, "Cargo criado com sucesso."
    except Exception as e:
        cursor.close()
        return False, f"Erro ao criar cargo: {e}"


def get_cardapio() -> list[dict]:
    """Recolhe todos os itens do cardápio com informações de stock."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.nome, c.valor, s.stock 
        FROM cardapio c 
        JOIN stock s ON c.stock_id = s.id
    """)
    results = cursor.fetchall()
    cursor.close()
    return [{"id": item_id, "nome": nome, "preco": float(preco), "stock": stock} for item_id, nome, preco, stock in results]


def add_cardapio_item(nome: str, preco: float, stock: int = 0) -> Tuple[bool, str]:
    """Adiciona um novo item ao cardápio."""
    try:
        print(f"[DEBUG] add_cardapio_item: nome='{nome}', preco={preco}, stock={stock}")
        food_available = check_food(nome)
        print(f"[DEBUG] check_food('{nome}') = {food_available}")
        if not food_available:
            return False, "Já existe um item com esse nome."
        add_food(preco, nome, stock)
        print(f"[DEBUG] add_food executado com sucesso")
        return True, "Item adicionado ao cardápio com sucesso."
    except Exception as e:
        print(f"[DEBUG] Erro em add_cardapio_item: {e}")
        return False, f"Erro ao adicionar item: {e}"


def update_cardapio_item(item_id: int, novo_preco: float = None) -> Tuple[bool, str]:
    """Actualiza o preço de um item do cardápio."""
    try:
        if novo_preco is not None:
            edit_price(item_id, novo_preco)
        return True, "Item actualizado com sucesso."
    except Exception as e:
        return False, f"Erro ao actualizar item: {e}"


def delete_cardapio_item(item_id: int) -> Tuple[bool, str]:
    """Remove um item do cardápio."""
    try:
        remove_food(item_id)
        return True, "Item removido com sucesso."
    except Exception as e:
        return False, f"Erro ao remover item: {e}"


def get_stock() -> list[dict]:
    """Recolhe todos os itens do stock."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, stock FROM stock")
    results = cursor.fetchall()
    cursor.close()
    return [{"id": item_id, "nome": nome, "quantidade": quantidade} for item_id, nome, quantidade in results]


def update_stock(item_id: int, nova_quantidade: int) -> Tuple[bool, str]:
    """Actualiza a quantidade em stock de um item."""
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE stock SET stock = %s WHERE id = %s", (nova_quantidade, item_id))
        conn.commit()
        cursor.close()
        return True, "Stock actualizado com sucesso."
    except Exception as e:
        cursor.close()
        return False, f"Erro ao actualizar stock: {e}"


def criar_pedido(user_id: int, itens: list[dict]) -> Tuple[bool, str]:
    """Cria um novo pedido para o utilizador."""
    cursor = conn.cursor()
    try:
        # Primeiro verificar stock de todos os itens antes de fazer alterações
        for item in itens:
            comida_id = item.get("comida_id")
            quantidade = item.get("quantidade", 1)
            
            cursor.execute("SELECT stock, nome FROM stock WHERE id = %s", (comida_id,))
            stock_result = cursor.fetchone()
            if not stock_result:
                cursor.close()
                return False, f"Item {comida_id} não encontrado."
            if stock_result[0] < quantidade:
                cursor.close()
                return False, f"Stock insuficiente para '{stock_result[1]}'. Disponível: {stock_result[0]}, Pedido: {quantidade}."
        
        # Obter próximo ID de fatura (agrupar itens do mesmo pedido)
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM fatura")
        fatura_id = cursor.fetchone()[0]
        
        # Adicionar cada item como uma linha na fatura
        for item in itens:
            comida_id = item.get("comida_id")
            quantidade = item.get("quantidade", 1)
            
            # Inserir item na fatura
            cursor.execute("INSERT INTO fatura (id, comida_id, quantidade) VALUES (%s, %s, %s)", (fatura_id, comida_id, quantidade))
            
            # Decrementar stock
            cursor.execute("UPDATE stock SET stock = stock - %s WHERE id = %s", (quantidade, comida_id))
        
        # Criar recibo
        cursor.execute("INSERT INTO recibo (fatura_id, conta_id, data) VALUES (%s, %s, NOW())", (fatura_id, user_id))
        conn.commit()
        cursor.close()
        return True, f"Pedido criado com sucesso. Fatura #{fatura_id}"
    except Exception as e:
        conn.rollback()
        cursor.close()
        return False, f"Erro ao criar pedido: {e}"


def get_historico_pedidos(user_id: int) -> list[dict]:
    """Recolhe o histórico de pedidos de um utilizador."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.fatura_id, r.data, f.comida_id, f.quantidade, s.nome, c.valor
        FROM recibo r
        JOIN fatura f ON r.fatura_id = f.id
        JOIN stock s ON f.comida_id = s.id
        JOIN cardapio c ON c.stock_id = s.id
        WHERE r.conta_id = %s
        ORDER BY r.data DESC
    """, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    pedidos = []
    for fatura_id, data, comida_id, quantidade, nome, valor in results:
        pedidos.append({
            "fatura_id": fatura_id,
            "data": data.strftime("%Y-%m-%d %H:%M:%S") if data else None,
            "item": nome,
            "quantidade": quantidade,
            "preco_unitario": float(valor),
            "total": float(valor) * quantidade
        })
    return pedidos