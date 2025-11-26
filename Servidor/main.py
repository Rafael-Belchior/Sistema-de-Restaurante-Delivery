import json
import socket
import threading
from typing import Optional, Tuple

from DB_Handler import authenticate_account, bootstrap_defaults, create_account

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


def handle_client(connection: socket.socket, address: Tuple[str, int]) -> None:
    # Trata múltiplos pedidos da mesma ligação de cliente
    print(f"Cliente conectado: {address}")
    global clients
    
    try:
        while True:  # Loop para lidar com múltiplos pedidos
            raw_payload = connection.recv(4096)
            if not raw_payload:  # Ligação fechada pelo cliente
                clients.pop(connection)
                break
            

            clients.update({connection: -1})

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
