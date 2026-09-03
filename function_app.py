import azure.functions as func
import logging
import json
import os

from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError

app = func.FunctionApp()

# Cliente da tabela usada para controle de idempotência.
# A tabela é criada automaticamente se ainda não existir.
_table_service = TableServiceClient.from_connection_string(
    os.environ["AZURE_TABLES_CONNECTION"]
)
_processed_orders = _table_service.create_table_if_not_exists("ProcessedOrders")


@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="orders",
    connection="SERVICE_BUS_CONNECTION"
)
def processar_pedido(msg: func.ServiceBusMessage):
    logging.info("Mensagem recebida do Service Bus.")

    try:
        dados = json.loads(msg.get_body().decode("utf-8"))
        order_id = dados.get("order_id")

        # Idempotência: a inserção na tabela só funciona uma vez por order_id.
        # Se o pedido já foi processado (reentrega, retry duplicado etc.),
        # a criação da entidade falha com ResourceExistsError e a gente
        # simplesmente ignora, sem reprocessar.
        try:
            _processed_orders.create_entity({
                "PartitionKey": "orders",
                "RowKey": order_id
            })
        except ResourceExistsError:
            logging.info(f"Pedido {order_id} já processado. Ignorando (idempotência).")
            return

        logging.info(
            f"Pedido recebido: {order_id} | "
            f"Cliente: {dados.get('cliente')} | "
            f"Valor: {dados.get('valor')}"
        )

    except Exception as erro:
        logging.error(f"Erro ao processar mensagem: {erro}")


@app.route(route="reserve", auth_level=func.AuthLevel.ANONYMOUS)
def reserve(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Executando reserva.")

    try:
        dados = req.get_json()
        order_id = dados.get("order_id")

        return func.HttpResponse(
            json.dumps({
                "order_id": order_id,
                "status": "reserved"
            }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as erro:
        logging.error(f"Erro na reserva: {erro}")

        return func.HttpResponse(
            json.dumps({"erro": "Falha ao reservar pedido"}),
            mimetype="application/json",
            status_code=400
        )


@app.route(route="charge", auth_level=func.AuthLevel.ANONYMOUS)
def charge(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Executando pagamento.")

    try:
        dados = req.get_json()
        order_id = dados.get("order_id")

        return func.HttpResponse(
            json.dumps({
                "order_id": order_id,
                "status": "charged"
            }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as erro:
        logging.error(f"Erro no pagamento: {erro}")

        return func.HttpResponse(
            json.dumps({"erro": "Falha ao realizar pagamento"}),
            mimetype="application/json",
            status_code=400
        )


@app.route(route="ship", auth_level=func.AuthLevel.ANONYMOUS)
def ship(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Executando envio.")

    try:
        dados = req.get_json()
        order_id = dados.get("order_id")

        return func.HttpResponse(
            json.dumps({
                "order_id": order_id,
                "status": "shipped"
            }),
            mimetype="application/json",
            status_code=200
        )

    except Exception as erro:
        logging.error(f"Erro no envio: {erro}")

        return func.HttpResponse(
            json.dumps({"erro": "Falha ao enviar pedido"}),
            mimetype="application/json",
            status_code=400
        )
