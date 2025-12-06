import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Get connection string from environment variable
conn_str = os.getenv('SERVICEBUS_CONNECTION_STRING')
if not conn_str:
    raise ValueError("SERVICEBUS_CONNECTION_STRING environment variable is not set")

queue_name = "orders-queue"

with ServiceBusClient.from_connection_string(conn_str) as client:
    sender = client.get_queue_sender(queue_name)
    with sender:
        msg = ServiceBusMessage("Hello from Cloudnautic Project!>")
        sender.send_messages(msg)
        print("Message sent successfully!")

