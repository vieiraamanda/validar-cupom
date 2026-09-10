# Checkpoint 4 — Observabilidade e Otimização

Projeto desenvolvido para o Checkpoint 4, utilizando Azure Functions, Azure Service Bus, Azure Logic Apps, Azure Table Storage e Azure Monitor.

## Observabilidade

A aplicação foi instrumentada com logs estruturados em JSON, permitindo acompanhar as principais etapas do processamento.

Principais eventos registrados:

* `service_bus_message_received`
* `order_processed`
* `duplicate_order`
* `function_execution`
* `function_error`

A observabilidade utiliza **Application Insights, Azure Monitor e Log Analytics**, permitindo consultar logs, requisições, falhas e métricas de desempenho.

Exemplos de consultas:

```kusto
traces
| where message contains "function_execution"
| order by timestamp desc
```

```kusto
traces
| where message contains "function_error"
| order by timestamp desc
```

```kusto
requests
| order by timestamp desc
| take 20
```

## Otimizações analisadas

### 1. Redução de logs desnecessários

Manter apenas eventos relevantes reduz o volume de telemetria, o custo de armazenamento e o ruído durante a análise.

### 2. Otimização de retry

Aplicar retry principalmente a falhas transitórias, como timeouts e erros 5xx, evitando novas tentativas para falhas permanentes.

Isso reduz chamadas desnecessárias e melhora a latência em cenários de erro.

### 3. Maior desacoplamento por eventos

Ampliar o uso do Azure Service Bus entre etapas do processamento pode reduzir o acoplamento entre serviços e melhorar escalabilidade e resiliência.

## Evidências

Os screenshots de logs e métricas estão disponíveis em:

```text
evidencias/checkpoint-4/
```
