import json
import socket
from getpass import getpass
from jsonFormat import Data

ENCODING = "utf-8"
SERVIDOR = ("127.0.0.1", 5000)

# Global persistent connection
client_socket: socket.socket = None


def _is_connected() -> bool:
    """Verifica se a conexão ainda está ativa"""
    try:
        if client_socket is None:
            return False
        client_socket.send(b'')
        return True
    except:
        return False


def conectar_servidor() -> bool:
    """Estabelece uma conexão persistente com o servidor"""
    global client_socket
    try:
        if client_socket is None or not _is_connected():
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(SERVIDOR)
            print("✓ Conectado ao servidor")
        return True
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        client_socket = None
        return False


def desconectar_servidor() -> None:
    """Fecha a conexão persistente com o servidor"""
    global client_socket
    if client_socket:
        try:
            client_socket.close()
        except:
            pass
        client_socket = None
        print("✓ Desconectado do servidor")


def enviar_pedido(payload: dict) -> dict:
    # Reutiliza a ligação persistente para enviar pedidos em formato JSON
    global client_socket
    if not conectar_servidor():
        raise ConnectionRefusedError("Não foi possível conectar ao servidor")
    
    try:
        client_socket.sendall(json.dumps(payload).encode(ENCODING))
        resposta = client_socket.recv(4096)
        return json.loads(resposta.decode(ENCODING))
    except Exception as e:
        client_socket = None  # Reset on error
        raise


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
        fluxo_comandos()

def fluxo_comandos() -> None:
    # Executa um fluxo simples de comandos após o login
    while True:
        print("\nEscolha uma opção:")
        print("1 - Ver perfil")
        print("0 - Sair")
        opcao = input("Opção: ").strip()

        if opcao == "1":
            response = enviar_pedido(Data(action="ver_perfil").to_dict())
            perfil = response.get("data", {}).get("perfil", {})
            username = perfil.get("username", "Desconhecido")
            cargo_nome = perfil.get("cargo_nome", "Desconhecido")
            print(f"Perfil do utilizador:")
            print(f"  Nome de utilizador: {username}")
            print(f"  Cargo: {cargo_nome}")

        elif opcao == "0":
            print("A terminar sessão...")
            break
        else:
            print("Opção inválida. Tente novamente.")

def fluxo_registo() -> None:
    # Pede os dados de registo e tenta criar uma nova conta remotamente
    username, password = recolher_credenciais()
    data = Data(action="registo", data={"username": username, "password": password})
    resposta = enviar_pedido(data.to_dict())
    print(resposta.get("mensagem", "Sem resposta."))