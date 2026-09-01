# Checkpoint 3 — Orquestração de Serviços Serverless

## Descrição

Projeto desenvolvido para demonstrar uma arquitetura serverless orientada a eventos utilizando Azure Functions, Azure Service Bus e Azure Logic Apps.

O Checkpoint 3 evolui a solução anterior adicionando uma orquestração de serviços, na qual as etapas de processamento são executadas em uma sequência definida por um workflow.

## Provedor Utilizado

* Microsoft Azure

## Arquitetura

O fluxo principal é composto pelas seguintes etapas:

1. Uma requisição HTTP inicia o workflow.
2. A Logic App executa a função `reserve`.
3. Após o sucesso de `reserve`, executa a função `charge`.
4. Após o sucesso de `charge`, executa a função `ship`.
5. As chamadas possuem política de retry com intervalo exponencial para tratar falhas temporárias.

Fluxo:

```text
HTTP Trigger
     |
     v
  reserve
     |
     v
  charge
     |
     v
   ship
```

## Funções Serverless

As funções foram implementadas utilizando Azure Functions com Python:

* `reserve` — responsável pela etapa de reserva.
* `charge` — responsável pela etapa de cobrança.
* `ship` — responsável pela etapa de envio.
* `processar_pedido` — função orientada a eventos acionada por mensagens da fila `orders` do Azure Service Bus.

## Orquestração

A orquestração é realizada utilizando Azure Logic Apps com estado.

As funções `reserve`, `charge` e `ship` são chamadas sequencialmente. Uma etapa somente é executada após a conclusão da etapa anterior.

## Retry

As três chamadas HTTP da orquestração utilizam política de retry com **Exponential Interval**.

Essa configuração permite novas tentativas em situações de falhas temporárias, como respostas HTTP 408, 429 e erros 5xx, além de determinadas falhas de conectividade.

## Azure Service Bus

O projeto também utiliza Azure Service Bus para processamento orientado a eventos.

A fila utilizada é:

```text
orders
```

A função `processar_pedido` é acionada quando uma nova mensagem é disponibilizada nessa fila.

A fila possui limite de **10 tentativas de entrega** (`maxDeliveryCount = 10`). Após exceder esse limite, mensagens que não conseguem ser processadas podem ser encaminhadas para a Dead-Letter Queue (DLQ) do Service Bus.

## Idempotência

A solução utiliza uma tabela `ProcessedOrders` no Azure Table Storage como estrutura de persistência para controle de pedidos processados.

A identificação dos pedidos é baseada no `order_id`, permitindo que o fluxo mantenha o registro dos pedidos processados e possa evitar o processamento duplicado.

## Como executar localmente

### Pré-requisitos

* Python 3.11 ou superior
* Azure Functions Core Tools
* Azure CLI

### Executar

Na pasta do projeto:

```bash
func start
```

As funções HTTP ficam disponíveis localmente em:

```text
http://localhost:7071/api/reserve
http://localhost:7071/api/charge
http://localhost:7071/api/ship
```

A função `processar_pedido` é acionada por mensagens do Azure Service Bus.

## Teste das funções

Exemplo de requisição para `reserve`:

```bash
curl -X POST http://localhost:7071/api/reserve \
  -H "Content-Type: application/json" \
  -d '{"order_id":"12345","cliente":"Amanda","valor":100}'
```

As funções `charge` e `ship` podem ser testadas de forma semelhante.

## Segurança

Nenhuma chave de acesso, credencial, segredo ou arquivo `.json` contendo credenciais deve ser versionado no repositório.

Configurações sensíveis são mantidas nas configurações do Azure ou em arquivos locais que não são enviados ao GitHub.

## Tecnologias utilizadas

* Python
* Azure Functions
* Azure Logic Apps
* Azure Service Bus
* Azure Table Storage
* Azure Cloud Shell
* Azure CLI
* Git
* GitHub
