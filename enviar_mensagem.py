import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

connection_string = os.environ["SERVICE_BUS_CONNECTION"]

with ServiceBusClient.from_connection_string(connection_string) as client:
    with client.get_queue_sender(queue_name="orders") as sender:
        mensagem = ServiceBusMessage(
            '{"order_id":"12345","cliente":"Amanda","valor":100}'
        )
        sender.send_messages(mensagem)

print("Mensagem enviada com sucesso!")
