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


def log_event(event, operation, order_id=None, status=None, error=None):
    """Registra eventos estruturados para observabilidade."""
    data = {
        "event": event,
        "operation": operation
    }

    if order_id is not None:
        data["order_id"] = order_id

    if status is not None:
        data["status"] = status

    if error is not None:
        data["error_type"] = type(error).__name__
        data["error_message"] = str(error)

    logging.info(json.dumps(data, ensure_ascii=False))


@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="orders",
    connection="SERVICE_BUS_CONNECTION"
)
def processar_pedido(msg: func.ServiceBusMessage):
    operation = "processar_pedido"
    order_id = None

    log_event(
        "service_bus_message_received",
        operation,
        status="started"
    )

    try:
        dados = json.loads(msg.get_body().decode("utf-8"))
        order_id = dados.get("order_id")

        log_event(
            "order_received",
            operation,
            order_id=order_id,
            status="processing"
        )

        # Idempotência: a inserção na tabela só funciona uma vez por order_id.
        # Se o pedido já foi processado, a criação da entidade falha com
        # ResourceExistsError e o pedido é ignorado.
        try:
            _processed_orders.create_entity({
                "PartitionKey": "orders",
                "RowKey": order_id
            })

        except ResourceExistsError:
            log_event(
                "duplicate_order",
                operation,
                order_id=order_id,
                status="ignored"
            )
            return

        log_event(
            "order_processed",
            operation,
            order_id=order_id,
            status="success"
        )

    except Exception as erro:
        log_event(
            "function_error",
            operation,
            order_id=order_id,
            status="error",
            error=erro
        )
        raise


@app.route(route="reserve", auth_level=func.AuthLevel.ANONYMOUS)
def reserve(req: func.HttpRequest) -> func.HttpResponse:
    operation = "reserve"
    order_id = None

    try:
        dados = req.get_json()
        order_id = dados.get("order_id")

        log_event(
            "function_execution",
            operation,
            order_id=order_id,
            status="started"
        )

        response = {
            "order_id": order_id,
            "status": "reserved"
        }

        log_event(
            "function_execution",
            operation,
            order_id=order_id,
            status="success"
        )

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )

    except Exception as erro:
        log_event(
            "function_error",
            operation,
            order_id=order_id,
            status="error",
            error=erro
        )

        return func.HttpResponse(
            json.dumps({"erro": "Falha ao reservar pedido"}),
            mimetype="application/json",
            status_code=400
        )


@app.route(route="charge", auth_level=func.AuthLevel.ANONYMOUS)
def charge(req: func.HttpRequest) -> func.HttpResponse:
    operation = "charge"
    order_id = None

    try:
        dados = req.get_json()
        order_id = dados.get("order_id")

        log_event(
            "function_execution",
            operation,
            order_id=order_id,
            status="started"
        )

        response = {
            "order_id": order_id,
            "status": "charged"
        }

        log_event(
            "function_execution",
            operation,
            order_id=order_id,
            status="success"
        )

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )

    except Exception as erro:
        log_event(
            "function_error",
            operation,
            order_id=order_id,
            status="error",
            error=erro
        )

        return func.HttpResponse(
            json.dumps({"erro": "Falha ao realizar pagamento"}),
            mimetype="application/json",
            status_code=400
        )


@app.route(route="ship", auth_level=func.AuthLevel.ANONYMOUS)
def ship(req: func.HttpRequest) -> func.HttpResponse:
    operation = "ship"
    order_id = None

    try:
        dados = req.get_json()
        order_id = dados.get("order_id")

        log_event(
            "function_execution",
            operation,
            order_id=order_id,
            status="started"
        )

        response = {
            "order_id": order_id,
            "status": "shipped"
        }

        log_event(
            "function_execution",
            operation,
            order_id=order_id,
            status="success"
        )

        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )

    except Exception as erro:
        log_event(
            "function_error",
            operation,
            order_id=order_id,
            status="error",
            error=erro
        )

        return func.HttpResponse(
            json.dumps({"erro": "Falha no envio"}),
            mimetype="application/json",
            status_code=400
        )
