from serverCalls import *

def main() -> None:
    # Ciclo principal com um menu simples para escolher a operação desejada
    print("Cliente de Autenticação - Restaurante Delivery")
    try:
        conectar_servidor()  # Conecta uma única vez no início
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
    except ConnectionRefusedError:
        print("Não foi possível ligar ao servidor. Verifique se está a correr.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        desconectar_servidor()


if __name__ == "__main__":
    # Permite executar o cliente directamente pela linha de comandos
    main()