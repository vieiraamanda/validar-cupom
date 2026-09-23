import azure.functions as func
import logging
import json
import os

from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError
from google import genai
from google.genai import types

app = func.FunctionApp()

# Cliente da tabela usada para controle de idempotência.
# A tabela é criada automaticamente se ainda não existir.
_table_service = TableServiceClient.from_connection_string(
    os.environ["AZURE_TABLES_CONNECTION"]
)
_processed_orders = _table_service.create_table_if_not_exists("ProcessedOrders")

_genai_client = genai.Client(api_key=os.environ["GOOGLE_AI_API_KEY"])


def consultar_historico_cliente(cliente: str) -> int:
    """Retorna quantos pedidos esse cliente já fez no histórico do sistema.

    Args:
        cliente: Nome do cliente.
    """
    filtro = f"Cliente eq '{cliente}'"
    return sum(1 for _ in _processed_orders.query_entities(filtro))


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


PROMPT_ELEGIBILIDADE = (
    "Pedido: order_id={order_id}, cliente={cliente}, valor=R${valor}. "
    "Política de elegibilidade: mais de 3 pedidos do mesmo cliente no histórico "
    "é padrão suspeito de uso indevido de cupom e deve ir para revisão manual; "
    "valores acima de R$5000 também vão para revisão manual por padrão. "
    "Consulte o histórico do cliente com a ferramenta disponível e decida. "
    "Responda em uma linha só, no formato: DECISAO: <APROVADO ou REVISAO_MANUAL> | MOTIVO: <justificativa curta>"
)


@app.route(route="verificar_elegibilidade", auth_level=func.AuthLevel.ANONYMOUS)
def verificar_elegibilidade(req: func.HttpRequest) -> func.HttpResponse:
    operation = "verificar_elegibilidade"
    order_id = None

    try:
        dados = req.get_json()
        order_id = dados.get("order_id")
        cliente = dados.get("cliente")
        valor = dados.get("valor")

        log_event("function_execution", operation, order_id=order_id, status="started")

        mensagem = PROMPT_ELEGIBILIDADE.format(order_id=order_id, cliente=cliente, valor=valor)

        # O SDK novo executa a ferramenta sozinho quando o modelo pede
        # (function calling automático), não precisa de loop manual aqui.
        resposta = _genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=mensagem,
            config=types.GenerateContentConfig(tools=[consultar_historico_cliente])
        )

        texto_final = resposta.text
        decisao = "APROVADO" if "APROVADO" in texto_final.upper() and "REVISAO_MANUAL" not in texto_final.upper() else "REVISAO_MANUAL"

        log_event("function_execution", operation, order_id=order_id, status="success")

        return func.HttpResponse(
            json.dumps({"order_id": order_id, "decisao": decisao, "justificativa": texto_final}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as erro:
        log_event("function_error", operation, order_id=order_id, status="error", error=erro)

        return func.HttpResponse(
            json.dumps({"erro": "Falha ao verificar elegibilidade"}),
            mimetype="application/json",
            status_code=400
        )
