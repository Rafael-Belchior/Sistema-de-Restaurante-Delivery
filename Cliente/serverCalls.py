import json
import socket
from getpass import getpass
from jsonFormat import Data

ENCODING = "utf-8"
SERVIDOR = ("127.0.0.1", 5000)


def enviar_pedido(payload: dict) -> dict:
    # Abre uma ligação temporária ao servidor para enviar pedidos em formato JSON
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(SERVIDOR)
        client_socket.sendall(json.dumps(payload).encode(ENCODING))
        resposta = client_socket.recv(4096)
    return json.loads(resposta.decode(ENCODING))


def recolher_credenciais() -> tuple[str, str]:
    # Solicita os dados necessários ao utilizador de forma interactiva
    username = input("Nome de utilizador: ").strip()
    password = getpass("Palavra-passe: ")
    return username, password


def fluxo_login() -> None:
    # Executa o fluxo de login e apresenta o resultado ao utilizador
    username, password = recolher_credenciais()
    data = Data(action="login", data={"username": username, "password": password})
    resposta = enviar_pedido(data.to_dict())
    print(resposta.get("mensagem", "Sem resposta."))
    if resposta.get("status") == "ok":
        dados = resposta.get("data", {})
        utilizador = dados.get("utilizador", {})
        print(f"Bem-vindo, {utilizador.get('username')} ({utilizador.get('cargo_nome')}).")


def fluxo_registo() -> None:
    # Pede os dados de registo e tenta criar uma nova conta remotamente
    username, password = recolher_credenciais()
    data = Data(action="registo", data={"username": username, "password": password})
    resposta = enviar_pedido(data.to_dict())
    print(resposta.get("mensagem", "Sem resposta."))