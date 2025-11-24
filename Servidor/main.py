import json
import socket
import threading
from typing import Optional, Tuple

from DB_Handler import authenticate_account, bootstrap_defaults, create_account

ENCODING = "utf-8"


def _build_response(status: str, message: str, data: Optional[dict] = None) -> bytes:
    # Constrói a resposta padronizada para o cliente com mensagens em português
    envelope = {"status": status, "mensagem": message}
    if data:
        envelope["data"] = data
    return json.dumps(envelope).encode(ENCODING)


def _handle_login(payload: dict) -> bytes:
    # Processa um pedido de login validando as credenciais recebidas
    username = payload.get("username", "").strip()
    password = payload.get("password", "")
    utilizador = authenticate_account(username, password)
    if not utilizador:
        return _build_response("erro", "Credenciais inválidas.")
    return _build_response("ok", "Login efectuado com sucesso.", {"utilizador": utilizador})


def _handle_register(payload: dict) -> bytes:
    # Trata os pedidos de criação de conta garantindo feedback claro ao cliente
    username = payload.get("username", "").strip()
    password = payload.get("password", "")
    sucesso, mensagem = create_account(username, password)
    status = "ok" if sucesso else "erro"
    return _build_response(status, mensagem)


def handle_client(connection: socket.socket, address: Tuple[str, int]) -> None:
    # Recebe uma conexão individual, interpreta o pedido e envia uma resposta
    with connection:
        payload: dict = None
        try:
            raw_payload = connection.recv(4096)
            if not raw_payload:
                return
            payload = json.loads(raw_payload.decode(ENCODING))
        except (json.JSONDecodeError, UnicodeDecodeError):
            connection.sendall(_build_response("erro", "Formato de mensagem inválido."))
            return

        acao = payload.get("action")

        print(acao)

        if acao == "login":
            resposta = _handle_login(payload)
        elif acao == "registo":
            resposta = _handle_register(payload)
        else:
            resposta = _build_response("erro", "Acção desconhecida.")
        connection.sendall(resposta)


def start_server(host: str = "0.0.0.0", port: int = 5000) -> None:
    # Inicializa o servidor TCP e escuta novas ligações em threads dedicadas
    bootstrap_defaults()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Servidor disponível em {host}:{port}")

    while True:
        client_conn, client_addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_conn, client_addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    # Arranque directo quando o ficheiro é executado manualmente
    start_server()
