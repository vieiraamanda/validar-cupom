#!/bin/bash
# Provisiona os recursos que sustentam a orquestração do checkpoint 3.
# Rodar via Azure Cloud Shell ou Azure CLI autenticado.
# Nenhuma credencial fica hardcoded aqui: RG, namespace e storage account
# são passados por variável de ambiente ou preenchidos antes de rodar.

set -e

RESOURCE_GROUP="${RESOURCE_GROUP:?defina RESOURCE_GROUP}"
SB_NAMESPACE="${SB_NAMESPACE:?defina SB_NAMESPACE}"
STORAGE_ACCOUNT="${STORAGE_ACCOUNT:?defina STORAGE_ACCOUNT}"

# Fila "orders" com dead-lettering automático após 10 tentativas de entrega.
az servicebus queue create \
  --resource-group "$RESOURCE_GROUP" \
  --namespace-name "$SB_NAMESPACE" \
  --name orders \
  --max-delivery-count 10 \
  --enable-dead-lettering-on-message-expiration true

# Tabela usada pela função processar_pedido para checar idempotência
# (create_table_if_not_exists no código também cobre isso, mas deixamos
# aqui como parte da infraestrutura documentada).
az storage table create \
  --name ProcessedOrders \
  --account-name "$STORAGE_ACCOUNT"

echo "Fila 'orders' (com DLQ) e tabela 'ProcessedOrders' provisionadas."
