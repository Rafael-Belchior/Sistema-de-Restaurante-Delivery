import json
import socket
import threading
from typing import Optional, Tuple

from DB_Handler import *

ENCODING = "utf-8"

clients: dict[socket.socket, int] = {}

def _build_response(status: str, message: str, data: Optional[dict] = None) -> bytes:
    # Constrói a resposta padronizada para o cliente com mensagens em português
    envelope = {"status": status, "mensagem": message}
    if data:
        envelope["data"] = data
    return json.dumps(envelope).encode(ENCODING)


def _handle_login(payload: dict, client_socket: socket.socket) -> bytes:
    # Processa um pedido de login validando as credenciais recebidas
    data: dict = payload.get("data", {})
    username = data.get("username", "").strip()
    password = data.get("password", "")
    utilizador = authenticate_account(username, password)
    if not utilizador:
        return _build_response("erro", "Credenciais inválidas.")
    
    # Regista o utilizador como autenticado na ligação actual usando o id do user
    global clients
    clients[client_socket] = utilizador["id"]

    return _build_response("ok", "Login efectuado com sucesso.", {"utilizador": utilizador})


def _handle_register(payload: dict) -> bytes:
    # Trata os pedidos de criação de conta garantindo feedback claro ao cliente
    data: dict = payload.get("data", {})
    username = data.get("username", "").strip()
    password = data.get("password", "")

    print(f"Pedido de registo recebido: username='{username}'")
    print(f"Password recebida: '{password}'")

    sucesso, mensagem = create_account(username, password)
    status = "ok" if sucesso else "erro"
    return _build_response(status, mensagem)

def get_user_from_socket(client_socket: socket.socket) -> Optional[dict]:
    global clients
    userID = clients.get(client_socket)
    return get_account_by_id(userID)


def handle_client(connection: socket.socket, address: Tuple[str, int]) -> None:
    # Trata múltiplos pedidos da mesma ligação de cliente
    print(f"Cliente conectado: {address}")
    global clients
    
    try:
        clients.update({connection: -1})
        while True:  # Loop para lidar com múltiplos pedidos
            raw_payload = connection.recv(4096)
            if not raw_payload:  # Ligação fechada pelo cliente
                clients.pop(connection)
                break

            try:
                payload: dict = json.loads(raw_payload.decode(ENCODING))
            except (json.JSONDecodeError, UnicodeDecodeError):
                connection.sendall(_build_response("erro", "Formato de mensagem inválido."))
                continue
            
            print(f"Pedido recebido de {address}: {payload}")
            acao = payload.get("action", "")

            if acao == "login":
                resposta = _handle_login(payload, connection)
            elif acao == "registo":
                resposta = _handle_register(payload)
            elif acao == "ver_perfil":
                perfil = get_user_from_socket(connection)
                if perfil is None:
                    resposta = _build_response("erro", "Utilizador não autenticado.")
                else:
                    # Aqui poderia ser implementada a lógica para obter o perfil do utilizador
                    resposta = _build_response("ok", "Perfil obtido com sucesso.", {"perfil": perfil})

            elif acao == "get_cargos":
                cargos = get_all_roles()
                resposta = _build_response("ok", "Cargos obtidos com sucesso.", cargos)

            elif acao == "del_cargo":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    data: dict = payload.get("data", {})
                    cargo_id = data.get("cargo_id")
                    if cargo_id is None:
                        resposta = _build_response("erro", "ID do cargo não fornecido.")
                    else:
                        sucesso, mensagem = delete_role(cargo_id)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            elif acao == "add_cargo":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    data: dict = payload.get("data", {})
                    nome = data.get("nome", "").strip()
                    if not nome:
                        resposta = _build_response("erro", "Nome do cargo é obrigatório.")
                    else:
                        sucesso, mensagem = create_role(nome)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            # Cardápio
            elif acao == "ver_cardapio":
                cardapio = get_cardapio()
                resposta = _build_response("ok", "Cardápio obtido com sucesso.", {"cardapio": cardapio})
            
            elif acao == "add_cardapio":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    data: dict = payload.get("data", {})
                    nome = data.get("nome", "").strip()
                    preco = data.get("preco")
                    stock = data.get("stock", 0)
                    if not nome or preco is None:
                        resposta = _build_response("erro", "Nome e preço são obrigatórios.")
                    else:
                        sucesso, mensagem = add_cardapio_item(nome, preco, stock)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            elif acao == "edit_cardapio":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    data: dict = payload.get("data", {})
                    item_id = data.get("item_id")
                    novo_preco = data.get("preco")
                    if item_id is None:
                        resposta = _build_response("erro", "ID do item é obrigatório.")
                    else:
                        sucesso, mensagem = update_cardapio_item(item_id, novo_preco)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            elif acao == "del_cardapio":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    data: dict = payload.get("data", {})
                    item_id = data.get("item_id")
                    if item_id is None:
                        resposta = _build_response("erro", "ID do item é obrigatório.")
                    else:
                        sucesso, mensagem = delete_cardapio_item(item_id)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            # Pedidos
            elif acao == "fazer_pedido":
                user_id = clients.get(connection)
                if user_id is None or user_id == -1:
                    resposta = _build_response("erro", "Utilizador não autenticado.")
                else:
                    data: dict = payload.get("data", {})
                    itens = data.get("itens", [])
                    if not itens:
                        resposta = _build_response("erro", "Nenhum item no pedido.")
                    else:
                        sucesso, mensagem = criar_pedido(user_id, itens)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
            
            elif acao == "ver_historico":
                user_id = clients.get(connection)
                if user_id is None or user_id == -1:
                    resposta = _build_response("erro", "Utilizador não autenticado.")
                else:
                    historico = get_historico_pedidos(user_id)
                    resposta = _build_response("ok", "Histórico obtido com sucesso.", {"historico": historico})
            
            # Stock
            elif acao == "ver_stock":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    stock = get_stock()
                    resposta = _build_response("ok", "Stock obtido com sucesso.", {"stock": stock})
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            elif acao == "edit_stock":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    data: dict = payload.get("data", {})
                    item_id = data.get("item_id")
                    quantidade = data.get("quantidade")
                    if item_id is None or quantidade is None:
                        resposta = _build_response("erro", "ID do item e quantidade são obrigatórios.")
                    else:
                        sucesso, mensagem = update_stock(item_id, quantidade)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            # Utilizadores
            elif acao == "ver_utilizadores":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    utilizadores = get_all_accounts()
                    resposta = _build_response("ok", "Utilizadores obtidos com sucesso.", {"utilizadores": utilizadores})
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            elif acao == "edit_utilizador":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    data: dict = payload.get("data", {})
                    target_id = data.get("user_id")
                    new_username = data.get("username")
                    new_password = data.get("password")
                    new_role_id = data.get("cargo_id")
                    if target_id is None:
                        resposta = _build_response("erro", "ID do utilizador é obrigatório.")
                    else:
                        sucesso, mensagem = update_account(target_id, new_username, new_password, new_role_id)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            elif acao == "del_utilizador":
                user_id = clients.get(connection)
                if (user_id is not None and user_id != -1) and is_admin(user_id):
                    data: dict = payload.get("data", {})
                    target_id = data.get("user_id")
                    if target_id is None:
                        resposta = _build_response("erro", "ID do utilizador é obrigatório.")
                    else:
                        sucesso, mensagem = delete_account(target_id)
                        status = "ok" if sucesso else "erro"
                        resposta = _build_response(status, mensagem)
                else:
                    resposta = _build_response("erro", "Permissão negada.")
            
            elif acao == "atualizar_conta":
                user_id = clients.get(connection)
                if user_id is None or user_id == -1:
                    resposta = _build_response("erro", "Utilizador não autenticado.")
                else:
                    data: dict = payload.get("data", {})
                    new_password = data.get("password")
                    sucesso, mensagem = update_account(user_id, new_password=new_password)
                    status = "ok" if sucesso else "erro"
                    resposta = _build_response(status, mensagem)
            
            else:
                resposta = _build_response("erro", "Acção desconhecida.")
            
            connection.sendall(resposta)
    
    except Exception as e:
        print(f"Erro ao processar cliente {address}: {e}")
    finally:
        connection.close()
        print(f"Cliente desconectado: {address}")


def start_server(host: str = "0.0.0.0", port: int = 5000) -> None:
    # Inicializa o servidor TCP e escuta novas ligações em threads dedicadas
    bootstrap_defaults()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Servidor disponível em {host}:{port}")

    try:
        while True:
            client_conn, client_addr = server_socket.accept()
            # Uma thread por cliente, lida com múltiplos pedidos
            thread = threading.Thread(target=handle_client, args=(client_conn, client_addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nServidor encerrado")
    finally:
        server_socket.close()

if __name__ == "__main__":
    # Arranque directo quando o ficheiro é executado manualmente
    start_server()
