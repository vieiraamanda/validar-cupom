import azure.functions as func
import logging
import json

app = func.FunctionApp()


@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="orders",
    connection="SERVICE_BUS_CONNECTION"
)
def processar_pedido(msg: func.ServiceBusMessage):
    logging.info("Mensagem recebida do Service Bus.")

    try:
        dados = json.loads(msg.get_body().decode("utf-8"))

        logging.info(
            f"Pedido recebido: {dados.get('order_id')} | "
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
