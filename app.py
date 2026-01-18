import streamlit as st
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Azure Service Bus Manager",
    page_icon="📬",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #0078D4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown('<h1 class="main-header">📬 Azure Service Bus Manager</h1>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Connection string input
    conn_str = st.text_input(
        "Service Bus Connection String",
        value=os.getenv('SERVICEBUS_CONNECTION_STRING', ''),
        type="password",
        help="Enter your Azure Service Bus connection string"
    )
    
    # Queue name input
    queue_name = st.text_input(
        "Queue Name",
        value="orders-queue",
        help="Enter the name of your Service Bus queue"
    )
    
    st.divider()
    
    # Statistics
    st.header("📊 Statistics")
    if st.session_state.messages:
        st.metric("Messages Received", len(st.session_state.messages))
    else:
        st.info("No messages received yet")
    
    st.divider()
    
    # Clear history
    if st.button("🗑️ Clear Message History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Send Message", "📥 Receive Messages", "🗑️ Delete Messages", "ℹ️ About"])

# Tab 1: Send Message
with tab1:
    st.header("Send Message to Queue")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        message_text = st.text_area(
            "Message Content",
            placeholder="Enter your message here...",
            height=150,
            help="Enter the message you want to send to the Service Bus queue"
        )
    
    with col2:
        st.write("**Message Properties (Optional)**")
        msg_id = st.text_input("Message ID", placeholder="Auto-generated if empty")
        content_type = st.text_input("Content Type", value="text/plain")
        session_id = st.text_input("Session ID (Optional)", placeholder="Leave empty for non-session queue")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        send_button = st.button("📤 Send Message", type="primary", use_container_width=True)
    
    if send_button:
        if not conn_str:
            st.error("⚠️ Please enter a connection string in the sidebar")
        elif not message_text:
            st.error("⚠️ Please enter a message to send")
        else:
            try:
                with ServiceBusClient.from_connection_string(conn_str) as client:
                    sender = client.get_queue_sender(queue_name)
                    with sender:
                        # Create message
                        msg = ServiceBusMessage(message_text)
                        if msg_id:
                            msg.message_id = msg_id
                        if content_type:
                            msg.content_type = content_type
                        if session_id:
                            msg.session_id = session_id
                        
                        sender.send_messages(msg)
                        st.success(f"✅ Message sent successfully to queue '{queue_name}'!")
                        
                        # Show message details
                        with st.expander("Message Details"):
                            st.json({
                                "content": message_text,
                                "message_id": msg.message_id or "Auto-generated",
                                "content_type": msg.content_type,
                                "timestamp": datetime.now().isoformat()
                            })
            except Exception as e:
                st.error(f"❌ Error sending message: {str(e)}")

# Tab 2: Receive Messages
with tab2:
    st.header("Receive Messages from Queue")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        max_messages = st.number_input("Max Messages", min_value=1, max_value=50, value=10)
        wait_time = st.number_input("Wait Time (seconds)", min_value=1, max_value=30, value=5)
        peek_only = st.checkbox("Peek Only (Don't Remove)", value=False)
    
    with col2:
        st.info("💡 **Tip:** Use 'Peek Only' to view messages without removing them from the queue. Otherwise, messages will be received and completed (removed).")
    
    if st.button("📥 Receive Messages", type="primary", use_container_width=True):
        if not conn_str:
            st.error("⚠️ Please enter a connection string in the sidebar")
        else:
            try:
                with st.spinner("Receiving messages..."):
                    with ServiceBusClient.from_connection_string(conn_str) as client:
                        receiver = client.get_queue_receiver(queue_name)
                        
                        with receiver:
                            if peek_only:
                                received_msgs = receiver.peek_messages(max_message_count=max_messages)
                                action = "peeked"
                            else:
                                received_msgs = receiver.receive_messages(
                                    max_message_count=max_messages,
                                    max_wait_time=wait_time
                                )
                                action = "received"
                            
                            if not received_msgs:
                                st.warning("📭 No messages found in the queue.")
                            else:
                                st.success(f"✅ {len(received_msgs)} message(s) {action}!")
                                
                                for idx, msg in enumerate(received_msgs, 1):
                                    with st.expander(f"Message {idx} - ID: {msg.message_id}"):
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.write("**Message Content:**")
                                            st.code(str(msg), language="text")
                                        
                                        with col2:
                                            st.write("**Properties:**")
                                            msg_data = {
                                                "Message ID": msg.message_id,
                                                "Content Type": msg.content_type,
                                                "Delivery Count": msg.delivery_count,
                                                "Enqueued Time": str(msg.enqueued_time_utc) if hasattr(msg, 'enqueued_time_utc') else "N/A",
                                                "Sequence Number": msg.sequence_number if hasattr(msg, 'sequence_number') else "N/A"
                                            }
                                            st.json(msg_data)
                                        
                                        # Complete message if not peeking
                                        if not peek_only:
                                            receiver.complete_message(msg)
                                            st.caption("✅ Message completed and removed from queue")
                                        
                                        # Add to session state
                                        st.session_state.messages.append({
                                            "content": str(msg),
                                            "id": msg.message_id,
                                            "timestamp": datetime.now().isoformat(),
                                            "action": action
                                        })
            except Exception as e:
                st.error(f"❌ Error receiving messages: {str(e)}")

# Tab 3: Delete Messages
with tab3:
    st.header("Delete Messages from Queue")
    
    st.warning("⚠️ **Warning:** This will receive and permanently delete messages from the queue.")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        delete_count = st.number_input("Max Messages to Delete", min_value=1, max_value=100, value=10)
        delete_wait_time = st.number_input("Wait Time (seconds)", min_value=1, max_value=30, value=5, key="delete_wait")
    
    with col2:
        st.info("💡 This operation will receive messages and immediately complete them, effectively deleting them from the queue.")
    
    confirm_delete = st.checkbox("I understand that this action cannot be undone")
    
    if st.button("🗑️ Delete Messages", type="secondary", disabled=not confirm_delete, use_container_width=True):
        if not conn_str:
            st.error("⚠️ Please enter a connection string in the sidebar")
        else:
            try:
                with st.spinner("Deleting messages..."):
                    with ServiceBusClient.from_connection_string(conn_str) as client:
                        receiver = client.get_queue_receiver(queue_name)
                        
                        with receiver:
                            received_msgs = receiver.receive_messages(
                                max_message_count=delete_count,
                                max_wait_time=delete_wait_time
                            )
                            
                            if not received_msgs:
                                st.info("📭 No messages found in the queue.")
                            else:
                                deleted_count = 0
                                for msg in received_msgs:
                                    receiver.complete_message(msg)
                                    deleted_count += 1
                                
                                st.success(f"✅ Successfully deleted {deleted_count} message(s) from queue '{queue_name}'!")
            except Exception as e:
                st.error(f"❌ Error deleting messages: {str(e)}")

# Tab 4: About
with tab4:
    st.header("About Azure Service Bus Manager")
    
    st.markdown("""
    This application provides a user-friendly interface for managing Azure Service Bus messages.
    
    ### Features
    - 📤 **Send Messages**: Send custom messages to your Service Bus queue
    - 📥 **Receive Messages**: Receive and view messages with peek or complete options
    - 🗑️ **Delete Messages**: Batch delete messages from the queue
    - 📊 **Statistics**: Track message operations
    
    ### How to Use
    1. Enter your **Service Bus Connection String** in the sidebar
    2. Specify your **Queue Name** (default: orders-queue)
    3. Use the tabs to send, receive, or delete messages
    
    ### Prerequisites
    - Azure Service Bus namespace
    - Valid connection string with appropriate permissions
    - Existing queue in your Service Bus namespace
    
    ### Environment Variables
    You can set the connection string as an environment variable:
    ```bash
    export SERVICEBUS_CONNECTION_STRING="your-connection-string"
    ```
    
    ### Running the Application
    ```bash
    streamlit run app.py
    ```
    
    ### Resources
    - [Azure Service Bus Documentation](https://learn.microsoft.com/azure/service-bus-messaging/)
    - [Python SDK Documentation](https://learn.microsoft.com/python/api/overview/azure/servicebus)
    """)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("SDK Version", "azure-servicebus")
    with col2:
        st.metric("Framework", "Streamlit")
    with col3:
        st.metric("Queue", queue_name)

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit and Azure Service Bus SDK")
