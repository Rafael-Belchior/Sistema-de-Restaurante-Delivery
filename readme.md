# 📝 Objetivo do Trabalho

## Desenvolver um Sistema de Restaurante Delivery utilizando Python, composto por:

### Aplicação Servidor
- Responsável por gerir pedidos, autenticação, cardápio, stock e histórico.

### Aplicação Cliente
- Permite a interação do utilizador com o sistema.

## O sistema deve obrigatoriamente utilizar:

- MySQL

- Sockets

- Herança

- Módulos

Todas as informações (utilizadores, funcionários, produtos, etc.) devem ser criadas durante a execução da aplicação.

# 👥 Papéis de Utilizador
## Administrador

- Gestão global do sistema

- Controlo de stock

- Gestão do cardápio

## Entregador

- Responsável pela entrega dos pedidos

## Cliente

- Encomenda refeições

# 🖥️ Aplicação Servidor

- Núcleo responsável por armazenar, validar e processar todas as operações comerciais.

1. 🔐 Autenticação

- Receber credenciais (utilizador/senha).

- Verificar tipo de utilizador (admin, entregador, cliente).

- Controlar permissões (ex: só admin adiciona produtos).

2. 🍽️ Gestão de Cardápio
Administrador

- Adicionar pratos

- Atualizar pratos

- Preço

- Stock

- Descrição

Retornos:

- ATUALIZACAO_OK

- PRODUTO_NAO_ENCONTRADO

- Remover pratos

- Retorno: PRODUTO_REMOVIDO

- Todos os utilizadores

- Listar produtos

- Lista completa

- Filtro por categoria, preço ou disponibilidade

3. 🛒 Gestão de Pedidos

- Registar pedido:

- Recebe ID do produto + quantidade

- Verifica stock

- Atualiza base de dados

Retornos:

- VENDA_CONFIRMADA

- STOCK_INSUFICIENTE

- Atualizar estado do pedido:

- Em preparação → Pronto para entrega → Entregue

- Consultar histórico de vendas

- Lista com datas e valores totais

- 4. 📦 Gestão de Stock

- Atualizar ingredientes usados

- Monitorizar stock (alerta abaixo de 5 unidades)

- Enviar alerta: ALERTA_STOCK_BAIXO

# 🖥️ Aplicação Cliente
1. 🔑 Login

- Enviar utilizador/senha

- Receber tipo de acesso

- Possibilidade de registo caso não exista conta

2. 🍜 Gestão de Cardápio (Administrador)
### Ações disponíveis:

- Adicionar prato

- Envia: ADD_PRATO

- Recebe:

- PRODUTO_ADICIONADO

- ERRO_DUPLICADO

- Atualizar prato

- Envia: 

- UPDATE_PRATO

- Recebe:

- ATUALIZACAO_OK

- PRODUTO_NAO_ENCONTRADO

- Remover prato

- Envia: 

- REMOVE_PRATO

- Recebe:

- PRODUTO_REMOVIDO

- Todos os utilizadores

- Listar pratos

- Envia: 

- LIST_PRATOS

 3. 🧾 Gestão de Pedidos

- Selecionar prato + quantidade

- Enviar pedido: 

- REGISTRAR_PEDIDO

- Receber retorno:

- VENDA_CONFIRMADA

- STOCK_INSUFICIENTE

- Histórico de pedidos (todos)

- Envia: - HISTORICO_PEDIDOS

4. 📉 Gestão de Stock (Administrador)

- Consultar stock: CONSULTAR_STOCK

- Receber alertas do servidor: 

- ALERTA_STOCK_BAIXO

- Atualizar stock: 

- ATUALIZAR_STOCK