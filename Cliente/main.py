from serverCalls import *

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