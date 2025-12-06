import os
from azure.servicebus import ServiceBusClient

# Get connection string from environment variable
conn_str = os.getenv('SERVICEBUS_CONNECTION_STRING')
if not conn_str:
    raise ValueError("SERVICEBUS_CONNECTION_STRING environment variable is not set")

queue_name = "orders-queue"

def receive_and_delete_messages():
    with ServiceBusClient.from_connection_string(conn_str) as client:
        receiver = client.get_queue_receiver(queue_name)
        
        with receiver:
            # Receive messages (max 10 at a time)
            received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
            
            if not received_msgs:
                print("No messages found in the queue.")
                return
            
            print(f"Received {len(received_msgs)} message(s):")
            
            for msg in received_msgs:
                print(f"Message: {str(msg)}")
                print(f"Message ID: {msg.message_id}")
                print(f"Content Type: {msg.content_type}")
                print(f"Delivery Count: {msg.delivery_count}")
                print("-" * 50)
                
                # Complete the message (this removes it from the queue)
                receiver.complete_message(msg)
                print("✅ Message deleted successfully!")
                print("-" * 50)

if __name__ == "__main__":
    print("🔍 Checking for messages in the queue...")
    receive_and_delete_messages()
    print("✨ Message processing completed!")