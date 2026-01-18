#!/usr/bin/env python3
"""
Command-Line Interface for Azure Service Bus Manager
A simple CLI alternative to the web UI
"""

import os
import sys
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from datetime import datetime

# ANSI color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header():
    """Print application header"""
    print(f"\n{BLUE}{BOLD}{'=' * 60}")
    print("     📬 Azure Service Bus Manager - CLI")
    print(f"{'=' * 60}{RESET}\n")

def print_menu():
    """Display main menu"""
    print(f"{BOLD}Main Menu:{RESET}")
    print("1. 📤 Send Message")
    print("2. 📥 Receive Messages")
    print("3. 👀 Peek Messages (without removing)")
    print("4. 🗑️  Delete Messages")
    print("5. ⚙️  Change Configuration")
    print("6. ❌ Exit")
    print()

def get_config():
    """Get configuration from environment or user input"""
    conn_str = os.getenv('SERVICEBUS_CONNECTION_STRING')
    queue_name = os.getenv('SERVICEBUS_QUEUE_NAME', 'orders-queue')
    
    if not conn_str:
        print(f"{YELLOW}⚠️  No connection string found in environment.{RESET}")
        conn_str = input("Enter Service Bus Connection String: ").strip()
    
    return conn_str, queue_name

def send_message(conn_str, queue_name):
    """Send a message to the queue"""
    print(f"\n{BOLD}Send Message{RESET}")
    print("-" * 40)
    
    message = input("Enter message content: ").strip()
    if not message:
        print(f"{RED}❌ Message cannot be empty{RESET}")
        return
    
    msg_id = input("Message ID (press Enter to auto-generate): ").strip()
    content_type = input("Content Type (default: text/plain): ").strip() or "text/plain"
    
    try:
        with ServiceBusClient.from_connection_string(conn_str) as client:
            sender = client.get_queue_sender(queue_name)
            with sender:
                msg = ServiceBusMessage(message)
                if msg_id:
                    msg.message_id = msg_id
                msg.content_type = content_type
                
                sender.send_messages(msg)
                print(f"\n{GREEN}✅ Message sent successfully!{RESET}")
                print(f"Queue: {queue_name}")
                print(f"Message ID: {msg.message_id}")
                print(f"Content Type: {msg.content_type}")
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")

def receive_messages(conn_str, queue_name, peek_only=False):
    """Receive messages from the queue"""
    action = "Peek" if peek_only else "Receive"
    print(f"\n{BOLD}{action} Messages{RESET}")
    print("-" * 40)
    
    max_count = input(f"Max messages to {action.lower()} (default: 10): ").strip()
    max_count = int(max_count) if max_count.isdigit() else 10
    
    wait_time = input("Wait time in seconds (default: 5): ").strip()
    wait_time = int(wait_time) if wait_time.isdigit() else 5
    
    try:
        with ServiceBusClient.from_connection_string(conn_str) as client:
            receiver = client.get_queue_receiver(queue_name)
            
            with receiver:
                if peek_only:
                    received_msgs = receiver.peek_messages(max_message_count=max_count)
                else:
                    received_msgs = receiver.receive_messages(
                        max_message_count=max_count,
                        max_wait_time=wait_time
                    )
                
                if not received_msgs:
                    print(f"\n{YELLOW}📭 No messages found in the queue{RESET}")
                    return
                
                print(f"\n{GREEN}✅ {len(received_msgs)} message(s) {action.lower()}ed!{RESET}\n")
                
                for idx, msg in enumerate(received_msgs, 1):
                    print(f"{BOLD}Message {idx}:{RESET}")
                    print(f"  Content: {str(msg)}")
                    print(f"  Message ID: {msg.message_id}")
                    print(f"  Content Type: {msg.content_type}")
                    print(f"  Delivery Count: {msg.delivery_count}")
                    if hasattr(msg, 'enqueued_time_utc'):
                        print(f"  Enqueued Time: {msg.enqueued_time_utc}")
                    print("-" * 40)
                    
                    if not peek_only:
                        receiver.complete_message(msg)
                        print(f"  {GREEN}✅ Message completed and removed{RESET}")
                        print("-" * 40)
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")

def delete_messages(conn_str, queue_name):
    """Delete messages from the queue"""
    print(f"\n{BOLD}Delete Messages{RESET}")
    print(f"{RED}⚠️  WARNING: This will permanently delete messages!{RESET}")
    print("-" * 40)
    
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Operation cancelled.")
        return
    
    max_count = input("Max messages to delete (default: 10): ").strip()
    max_count = int(max_count) if max_count.isdigit() else 10
    
    try:
        with ServiceBusClient.from_connection_string(conn_str) as client:
            receiver = client.get_queue_receiver(queue_name)
            
            with receiver:
                received_msgs = receiver.receive_messages(
                    max_message_count=max_count,
                    max_wait_time=5
                )
                
                if not received_msgs:
                    print(f"\n{YELLOW}📭 No messages found in the queue{RESET}")
                    return
                
                deleted_count = 0
                for msg in received_msgs:
                    receiver.complete_message(msg)
                    deleted_count += 1
                
                print(f"\n{GREEN}✅ Successfully deleted {deleted_count} message(s){RESET}")
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")

def change_config():
    """Change configuration"""
    print(f"\n{BOLD}Change Configuration{RESET}")
    print("-" * 40)
    
    new_conn_str = input("New Connection String (press Enter to keep current): ").strip()
    new_queue = input("New Queue Name (press Enter to keep current): ").strip()
    
    if new_conn_str:
        os.environ['SERVICEBUS_CONNECTION_STRING'] = new_conn_str
        print(f"{GREEN}✅ Connection string updated{RESET}")
    
    if new_queue:
        os.environ['SERVICEBUS_QUEUE_NAME'] = new_queue
        print(f"{GREEN}✅ Queue name updated to: {new_queue}{RESET}")

def main():
    """Main application loop"""
    print_header()
    
    conn_str, queue_name = get_config()
    
    if not conn_str:
        print(f"{RED}❌ Connection string is required. Exiting.{RESET}")
        sys.exit(1)
    
    print(f"{GREEN}✅ Connected to queue: {queue_name}{RESET}")
    
    while True:
        print()
        print_menu()
        
        choice = input(f"{BOLD}Select an option (1-6): {RESET}").strip()
        
        if choice == '1':
            send_message(conn_str, queue_name)
        elif choice == '2':
            receive_messages(conn_str, queue_name, peek_only=False)
        elif choice == '3':
            receive_messages(conn_str, queue_name, peek_only=True)
        elif choice == '4':
            delete_messages(conn_str, queue_name)
        elif choice == '5':
            change_config()
            conn_str, queue_name = get_config()
        elif choice == '6':
            print(f"\n{BLUE}👋 Goodbye!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}❌ Invalid option. Please try again.{RESET}")
        
        input(f"\n{BOLD}Press Enter to continue...{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{BLUE}👋 Goodbye!{RESET}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}❌ Fatal error: {e}{RESET}\n")
        sys.exit(1)
