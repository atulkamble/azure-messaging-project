import os
from azure.servicebus import ServiceBusClient

# Get connection string from environment variable
connection_string = os.environ.get('SERVICEBUS_CONNECTION_STRING')
queue_name = "orders-queue"

def receive_messages():
    """
    Receive and process messages from Azure Service Bus queue
    """
    # Create a Service Bus client
    servicebus_client = ServiceBusClient.from_connection_string(
        conn_str=connection_string,
        logging_enable=True
    )

    with servicebus_client:
        # Get the Queue Receiver
        receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
        
        with receiver:
            # Receive messages (max 10 messages, wait up to 5 seconds)
            received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
            
            if not received_msgs:
                print("No messages received from the queue.")
                return
            
            print(f"Received {len(received_msgs)} message(s)")
            
            for msg in received_msgs:
                print(f"\nMessage: {str(msg)}")
                print(f"Content Type: {msg.content_type}")
                print(f"Message ID: {msg.message_id}")
                print(f"Delivery Count: {msg.delivery_count}")
                
                # Complete the message to remove it from the queue
                receiver.complete_message(msg)
                print(f"Message completed and removed from queue")

if __name__ == "__main__":
    try:
        print("Starting to receive messages from Azure Service Bus queue...")
        receive_messages()
        print("\nMessage receiving completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
