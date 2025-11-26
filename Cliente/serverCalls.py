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
        print("2 - Ver cardápio")
        print("3 - Fazer pedido")
        print("4 - Ver histórico de pedidos")
        print("5 - Atualizar informações da conta")
        print("6 - Gerir cardápio (Admin)")
        print("7 - Gerir utilizadores (Admin)")
        print("8 - Gerir cargos (Admin)")
        print("9 - Gerir stock (Admin)")
        print()
        print("0 - Sair")
        opcao = input("Opção: ").strip()

        if opcao == "1":
            fluxo_ver_perfil()
        elif opcao == "2":
            fluxo_ver_cardapio()
        elif opcao == "3":
            fluxo_fazer_pedido()
        elif opcao == "4":
            fluxo_ver_historico()
        elif opcao == "5":
            fluxo_atualizar_conta()
        elif opcao == "6":
            fluxo_gerir_cardapio()
        elif opcao == "7":
            fluxo_gerir_utilizadores()
        elif opcao == "8":
            fluxo_gerir_cargos()
        elif opcao == "9":
            fluxo_gerir_stock()
        elif opcao == "0":
            print("A terminar sessão...")
            break
        else:
            print("Opção inválida. Tente novamente.")


def fluxo_ver_perfil() -> None:
    """Mostra o perfil do utilizador autenticado."""
    response = enviar_pedido(Data(action="ver_perfil").to_dict())
    if response.get("status") == "ok":
        perfil = response.get("data", {}).get("perfil", {})
        print(f"\nPerfil do utilizador:")
        print(f"  ID: {perfil.get('id', 'N/A')}")
        print(f"  Nome de utilizador: {perfil.get('username', 'Desconhecido')}")
        print(f"  Cargo: {perfil.get('cargo_nome', 'Desconhecido')}")
    else:
        print(response.get("mensagem", "Erro ao obter perfil."))


def fluxo_ver_cardapio() -> None:
    """Mostra o cardápio disponível."""
    response = enviar_pedido(Data(action="ver_cardapio").to_dict())
    if response.get("status") == "ok":
        cardapio = response.get("data", {}).get("cardapio", [])
        if not cardapio:
            print("\nO cardápio está vazio.")
            return
        print("\n--- CARDÁPIO ---")
        for item in cardapio:
            disponivel = "✓" if item.get("stock", 0) > 0 else "✗ (Esgotado)"
            print(f"  [{item.get('id')}] {item.get('nome')} - €{item.get('preco', 0):.2f} {disponivel}")
    else:
        print(response.get("mensagem", "Erro ao obter cardápio."))


def fluxo_fazer_pedido() -> None:
    """Permite ao utilizador fazer um pedido."""
    # Primeiro mostrar o cardápio
    response = enviar_pedido(Data(action="ver_cardapio").to_dict())
    if response.get("status") != "ok":
        print(response.get("mensagem", "Erro ao obter cardápio."))
        return
    
    cardapio = response.get("data", {}).get("cardapio", [])
    if not cardapio:
        print("\nO cardápio está vazio. Não é possível fazer pedidos.")
        return
    
    print("\n--- CARDÁPIO ---")
    for item in cardapio:
        disponivel = f"(Stock: {item.get('stock', 0)})" if item.get("stock", 0) > 0 else "(Esgotado)"
        print(f"  [{item.get('id')}] {item.get('nome')} - €{item.get('preco', 0):.2f} {disponivel}")
    
    itens_pedido = []
    while True:
        item_id = input("\nID do item (ou 'fim' para concluir): ").strip()
        if item_id.lower() == 'fim':
            break
        try:
            item_id = int(item_id)
            quantidade = input("Quantidade: ").strip()
            quantidade = int(quantidade) if quantidade else 1
            itens_pedido.append({"comida_id": item_id, "quantidade": quantidade})
            print(f"  ✓ Adicionado ao pedido.")
        except ValueError:
            print("  ✗ Entrada inválida.")
    
    if not itens_pedido:
        print("Pedido cancelado - nenhum item selecionado.")
        return
    
    response = enviar_pedido(Data(action="fazer_pedido", data={"itens": itens_pedido}).to_dict())
    print(response.get("mensagem", "Erro ao fazer pedido."))


def fluxo_ver_historico() -> None:
    """Mostra o histórico de pedidos do utilizador."""
    response = enviar_pedido(Data(action="ver_historico").to_dict())
    if response.get("status") == "ok":
        historico = response.get("data", {}).get("historico", [])
        if not historico:
            print("\nNão tem pedidos no histórico.")
            return
        print("\n--- HISTÓRICO DE PEDIDOS ---")
        for pedido in historico:
            print(f"  Fatura #{pedido.get('fatura_id')} - {pedido.get('data')}")
            print(f"    {pedido.get('item')} x{pedido.get('quantidade')} = €{pedido.get('total', 0):.2f}")
    else:
        print(response.get("mensagem", "Erro ao obter histórico."))


def fluxo_atualizar_conta() -> None:
    """Permite ao utilizador atualizar a sua palavra-passe."""
    print("\n--- ATUALIZAR CONTA ---")
    nova_password = getpass("Nova palavra-passe: ")
    if not nova_password:
        print("Operação cancelada.")
        return
    
    response = enviar_pedido(Data(action="atualizar_conta", data={"password": nova_password}).to_dict())
    print(response.get("mensagem", "Erro ao atualizar conta."))


def fluxo_gerir_cardapio() -> None:
    """Menu de gestão do cardápio (apenas admin)."""
    while True:
        print("\n--- GERIR CARDÁPIO ---")
        print("1 - Ver cardápio")
        print("2 - Adicionar item")
        print("3 - Editar preço")
        print("4 - Remover item")
        print("0 - Voltar")
        opcao = input("Opção: ").strip()
        
        if opcao == "1":
            fluxo_ver_cardapio()
        elif opcao == "2":
            nome = input("Nome do item: ").strip()
            preco = input("Preço: ").strip()
            stock = input("Stock inicial (default 0): ").strip()
            try:
                preco = float(preco)
                stock = int(stock) if stock else 0
                response = enviar_pedido(Data(action="add_cardapio", data={"nome": nome, "preco": preco, "stock": stock}).to_dict())
                print(response.get("mensagem"))
            except ValueError:
                print("Valores inválidos.")
        elif opcao == "3":
            item_id = input("ID do item: ").strip()
            novo_preco = input("Novo preço: ").strip()
            try:
                response = enviar_pedido(Data(action="edit_cardapio", data={"item_id": int(item_id), "preco": float(novo_preco)}).to_dict())
                print(response.get("mensagem"))
            except ValueError:
                print("Valores inválidos.")
        elif opcao == "4":
            item_id = input("ID do item a remover: ").strip()
            try:
                response = enviar_pedido(Data(action="del_cardapio", data={"item_id": int(item_id)}).to_dict())
                print(response.get("mensagem"))
            except ValueError:
                print("ID inválido.")
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def fluxo_gerir_utilizadores() -> None:
    """Menu de gestão de utilizadores (apenas admin)."""
    while True:
        print("\n--- GERIR UTILIZADORES ---")
        print("1 - Ver utilizadores")
        print("2 - Editar utilizador")
        print("3 - Eliminar utilizador")
        print("0 - Voltar")
        opcao = input("Opção: ").strip()
        
        if opcao == "1":
            response = enviar_pedido(Data(action="ver_utilizadores").to_dict())
            if response.get("status") == "ok":
                utilizadores = response.get("data", {}).get("utilizadores", [])
                print("\n--- UTILIZADORES ---")
                for u in utilizadores:
                    print(f"  [{u.get('id')}] {u.get('username')} - {u.get('cargo_nome')}")
            else:
                print(response.get("mensagem"))
        elif opcao == "2":
            user_id = input("ID do utilizador: ").strip()
            print("Deixe em branco para não alterar.")
            new_username = input("Novo username: ").strip() or None
            new_password = input("Nova password: ").strip() or None
            new_cargo = input("Novo cargo_id: ").strip()
            new_cargo = int(new_cargo) if new_cargo else None
            try:
                data = {"user_id": int(user_id)}
                if new_username:
                    data["username"] = new_username
                if new_password:
                    data["password"] = new_password
                if new_cargo:
                    data["cargo_id"] = new_cargo
                response = enviar_pedido(Data(action="edit_utilizador", data=data).to_dict())
                print(response.get("mensagem"))
            except ValueError:
                print("ID inválido.")
        elif opcao == "3":
            user_id = input("ID do utilizador a eliminar: ").strip()
            try:
                response = enviar_pedido(Data(action="del_utilizador", data={"user_id": int(user_id)}).to_dict())
                print(response.get("mensagem"))
            except ValueError:
                print("ID inválido.")
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def fluxo_gerir_cargos() -> None:
    """Menu de gestão de cargos (apenas admin)."""
    while True:
        print("\n--- GERIR CARGOS ---")
        print("1 - Ver cargos")
        print("2 - Adicionar cargo")
        print("3 - Eliminar cargo")
        print("0 - Voltar")
        opcao = input("Opção: ").strip()
        
        if opcao == "1":
            response = enviar_pedido(Data(action="get_cargos").to_dict())
            if response.get("status") == "ok":
                cargos = response.get("data", [])
                print("\n--- CARGOS ---")
                for c in cargos:
                    print(f"  [{c.get('id')}] {c.get('nome')}")
            else:
                print(response.get("mensagem"))
        elif opcao == "2":
            nome = input("Nome do novo cargo: ").strip()
            if nome:
                response = enviar_pedido(Data(action="add_cargo", data={"nome": nome}).to_dict())
                print(response.get("mensagem"))
            else:
                print("Nome é obrigatório.")
        elif opcao == "3":
            cargo_id = input("ID do cargo a eliminar: ").strip()
            try:
                response = enviar_pedido(Data(action="del_cargo", data={"cargo_id": int(cargo_id)}).to_dict())
                print(response.get("mensagem"))
            except ValueError:
                print("ID inválido.")
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


def fluxo_gerir_stock() -> None:
    """Menu de gestão de stock (apenas admin)."""
    while True:
        print("\n--- GERIR STOCK ---")
        print("1 - Ver stock")
        print("2 - Atualizar quantidade")
        print("0 - Voltar")
        opcao = input("Opção: ").strip()
        
        if opcao == "1":
            response = enviar_pedido(Data(action="ver_stock").to_dict())
            if response.get("status") == "ok":
                stock = response.get("data", {}).get("stock", [])
                print("\n--- STOCK ---")
                for item in stock:
                    print(f"  [{item.get('id')}] {item.get('nome')} - Quantidade: {item.get('quantidade')}")
            else:
                print(response.get("mensagem"))
        elif opcao == "2":
            item_id = input("ID do item: ").strip()
            quantidade = input("Nova quantidade: ").strip()
            try:
                response = enviar_pedido(Data(action="edit_stock", data={"item_id": int(item_id), "quantidade": int(quantidade)}).to_dict())
                print(response.get("mensagem"))
            except ValueError:
                print("Valores inválidos.")
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")

def fluxo_registo() -> None:
    # Pede os dados de registo e tenta criar uma nova conta remotamente
    username, password = recolher_credenciais()
    data = Data(action="registo", data={"username": username, "password": password})
    resposta = enviar_pedido(data.to_dict())
    print(resposta.get("mensagem", "Sem resposta."))