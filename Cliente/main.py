import json
import socket
from getpass import getpass

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
    resposta = enviar_pedido({"action": "login", "username": username, "password": password})
    print(resposta.get("mensagem", "Sem resposta."))
    if resposta.get("status") == "ok":
        dados = resposta.get("dados", {})
        utilizador = dados.get("utilizador", {})
        print(f"Bem-vindo, {utilizador.get('username')} ({utilizador.get('cargo_nome')}).")


def fluxo_registo() -> None:
    # Pede os dados de registo e tenta criar uma nova conta remotamente
    username, password = recolher_credenciais()
    resposta = enviar_pedido({"action": "registo", "username": username, "password": password})
    print(resposta.get("mensagem", "Sem resposta."))


def main() -> None:
    # Ciclo principal com um menu simples para escolher a operação desejada
    print("Cliente de Autenticação - Restaurante Delivery")
    while True:
        print("\nEscolha uma opção:")
        print("1 - Login")
        print("2 - Registar nova conta")
        print("0 - Sair")
        opcao = input("Opção: ").strip()

        if opcao == "1":
            fluxo_login()
        elif opcao == "2":
            fluxo_registo()
        elif opcao == "0":
            print("A terminar...")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    # Permite executar o cliente directamente pela linha de comandos
    try:
        main()
    except ConnectionRefusedError:
        print("Não foi possível ligar ao servidor. Verifique se está a correr.")