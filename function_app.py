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
