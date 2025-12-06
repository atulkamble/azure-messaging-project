**Azure Messaging Project**. Since you’ve built AWS CloudWatch, RDS, DynamoDB, and Route53 projects before, I’ll frame this Azure project in the same way: a **hands-on end-to-end setup** with code, deployment steps, and explanations.

---

# 📩 Azure Messaging Project

## 🎯 Objective

A **hands-on Azure Service Bus messaging system** demonstrating **secure message publishing and consumption** using Python. This project showcases enterprise messaging patterns with **environment variable-based security** and real-world best practices.

## 🚀 Manual Setup & Run Instructions

### Prerequisites
- Azure CLI installed and logged in
- Python 3.7+ installed
- Git installed

### Step 1: Clone the Repository
```bash
git clone https://github.com/atulkamble/azure-messaging-project.git
cd azure-messaging-project
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Create Azure Resources
```bash
# Login to Azure (if not already logged in)
az login

# Create resource group
az group create --name messaging-rg --location eastus

# Create Service Bus namespace
az servicebus namespace create \
  --resource-group messaging-rg \
  --name cloudnautic-messaging-ns \
  --location eastus \
  --sku Standard

# Create queue
az servicebus queue create \
  --resource-group messaging-rg \
  --namespace-name cloudnautic-messaging-ns \
  --name orders-queue
```

### Step 4: Get Connection String
```bash
# Get the connection string
az servicebus namespace authorization-rule keys list \
  --resource-group messaging-rg \
  --namespace-name cloudnautic-messaging-ns \
  --name RootManageSharedAccessKey \
  --query "primaryConnectionString" -o tsv
```

### Step 5: Set Environment Variable
```bash
# Replace YOUR_CONNECTION_STRING with the output from Step 4
export SERVICEBUS_CONNECTION_STRING="YOUR_CONNECTION_STRING"

# For persistent setup, add to your shell profile (~/.zshrc or ~/.bashrc):
echo 'export SERVICEBUS_CONNECTION_STRING="YOUR_CONNECTION_STRING"' >> ~/.zshrc
source ~/.zshrc
```

### Step 6: Run the Project
```bash
# Send a message to the queue
python send_message.py

# Expected output: "Message sent successfully!"

# Receive and delete messages from the queue  
python delete_message.py

# Expected output: Shows received message details and confirms deletion
```

### Step 7: Verify in Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Resource Groups** → **messaging-rg**
3. Click on **cloudnautic-messaging-ns** Service Bus
4. Go to **Queues** → **orders-queue**
5. Use **Service Bus Explorer** to see messages in real-time

## 🔄 Testing the Message Flow

### Test 1: Send Multiple Messages
```bash
# Send several messages
for i in {1..5}; do python send_message.py; done
```

### Test 2: Batch Processing
```bash
# Check queue status
python delete_message.py
# This will show all messages and delete them
```

### Test 3: Error Handling
```bash
# Test without environment variable (should fail gracefully)
unset SERVICEBUS_CONNECTION_STRING
python send_message.py
# Should show: "SERVICEBUS_CONNECTION_STRING environment variable is not set"

# Reset the environment variable
export SERVICEBUS_CONNECTION_STRING="YOUR_CONNECTION_STRING"
```

## 🏗️ Project Architecture

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│  send_message.py│───▶│  Azure Service Bus   │◀───│delete_message.py│
│   (Producer)    │    │   orders-queue       │    │   (Consumer)    │
└─────────────────┘    └──────────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────────┐
                       │   Azure Portal       │
                       │ (Monitoring & Admin) │
                       └──────────────────────┘
```

**Components:**
- **Producer**: `send_message.py` - Sends messages to Service Bus queue
- **Message Broker**: Azure Service Bus queue - Stores and manages messages
- **Consumer**: `delete_message.py` - Receives and processes messages
- **Security**: Environment variables for connection strings (no hardcoded secrets)

## 📁 Project Files

| File | Purpose | Description |
|------|---------|-------------|
| `send_message.py` | Message Producer | Sends messages to Service Bus queue |
| `delete_message.py` | Message Consumer | Receives and deletes messages from queue |
| `requirements.txt` | Dependencies | Python packages (azure-functions, azure-servicebus) |
| `local.settings.json.template` | Azure Functions Config | Template for Azure Functions local development |
| `.env.template` | Environment Template | Template for environment variables |
| `.gitignore` | Git Exclusions | Prevents committing sensitive files |

## 🛠️ Development Workflow

### Option A: Quick Local Testing
```bash
# Set environment variable for current session
export SERVICEBUS_CONNECTION_STRING="your-connection-string-here"

# Test the workflow
python send_message.py && python delete_message.py
```

### Option B: Using .env File (Recommended)
```bash
# Copy template and edit with your connection string
cp .env.template .env
# Edit .env file with your actual connection string

# Load environment variables from .env (if using python-dotenv)
# pip install python-dotenv
# Then modify scripts to use: from dotenv import load_dotenv; load_dotenv()
```

## 🔍 Monitoring & Debugging

### Check Queue Status via Azure CLI
```bash
# Check queue details
az servicebus queue show \
  --resource-group messaging-rg \
  --namespace-name cloudnautic-messaging-ns \
  --name orders-queue \
  --query "{Name:name, MessageCount:messageCount, ActiveMessages:countDetails.activeMessageCount}"

# Check namespace status
az servicebus namespace show \
  --resource-group messaging-rg \
  --name cloudnautic-messaging-ns \
  --query "{Name:name, Status:status, Location:location}"
```

### Common Troubleshooting
```bash
# Test connection string format
echo $SERVICEBUS_CONNECTION_STRING

# Check if Azure CLI is logged in
az account show

# Verify Service Bus exists
az servicebus namespace list --query "[?name=='cloudnautic-messaging-ns']"
```

## 🧪 Advanced Testing Scenarios

### Test 1: Load Testing
```bash
# Send 100 messages
for i in {1..100}; do 
  python send_message.py && echo "Message $i sent"
done

# Process all messages
python delete_message.py
```

### Test 2: Error Simulation
```bash
# Test with invalid connection string
export SERVICEBUS_CONNECTION_STRING="invalid"
python send_message.py  # Should fail gracefully

# Reset to valid connection string
export SERVICEBUS_CONNECTION_STRING="your-valid-connection-string"
```

### Test 3: Concurrent Processing
```bash
# Terminal 1: Send messages continuously
while true; do python send_message.py; sleep 2; done

# Terminal 2: Process messages continuously  
while true; do python delete_message.py; sleep 5; done
```

## 🧹 Cleanup & Resource Management

### Delete Individual Resources
```bash
# Delete queue only
az servicebus queue delete \
  --resource-group messaging-rg \
  --namespace-name cloudnautic-messaging-ns \
  --name orders-queue

# Delete namespace (includes all queues)
az servicebus namespace delete \
  --resource-group messaging-rg \
  --name cloudnautic-messaging-ns
```

### Complete Cleanup
```bash
# Delete entire resource group and all resources
az group delete --name messaging-rg --yes --no-wait
```

## 🔐 Security Best Practices

### Environment Variables
- **Never commit connection strings** to version control
- Use **environment variables** or **Azure Key Vault** for secrets
- The `.gitignore` file prevents accidental commits of sensitive files

### Connection String Security
```bash
# ✅ Good: Use environment variables
export SERVICEBUS_CONNECTION_STRING="connection-string"

# ❌ Bad: Hardcode in source code
conn_str = "Endpoint=sb://namespace.servicebus.windows.net/..."
```

### Template Files Provided
- `.env.template` - Copy and customize for local development
- `local.settings.json.template` - Template for Azure Functions

## 📊 Production Considerations

### Scaling Patterns
- **Auto-scaling**: Configure based on queue depth
- **Dead Letter Queues**: Handle failed message processing
- **Partitioning**: Enable for high-throughput scenarios
- **Batch Processing**: Process multiple messages together

### Monitoring Setup
```bash
# Enable diagnostic settings
az monitor diagnostic-settings create \
  --resource /subscriptions/{subscription-id}/resourceGroups/messaging-rg/providers/Microsoft.ServiceBus/namespaces/cloudnautic-messaging-ns \
  --name "ServiceBusMetrics" \
  --logs '[{"category":"OperationalLogs","enabled":true}]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]' \
  --workspace /subscriptions/{subscription-id}/resourcegroups/messaging-rg/providers/microsoft.operationalinsights/workspaces/messaging-workspace
```

## 🚀 Next Steps & Extensions

### 1. Add Azure Functions Integration
```python
# function_app.py - Auto-process messages
import azure.functions as func
import logging

def main(msg: func.ServiceBusMessage):
    message_body = msg.get_body().decode('utf-8')
    logging.info(f'Processing message: {message_body}')
    # Add your business logic here
```

### 2. Add Dead Letter Queue Handling
```python
# Handle failed messages
def process_dead_letter_messages():
    dlq_receiver = client.get_queue_receiver(
        queue_name, 
        sub_queue=ServiceBusSubQueue.DEAD_LETTER
    )
    # Process dead letter messages
```

### 3. Add Message Filtering
```python
# Add message properties and filtering
msg = ServiceBusMessage(
    body="Order processed",
    application_properties={"order_type": "premium", "priority": "high"}
)
```

## 📚 Additional Resources

- **[Azure Service Bus Documentation](https://docs.microsoft.com/azure/service-bus-messaging/)**
- **[Python SDK Reference](https://docs.microsoft.com/python/api/azure-servicebus/)**
- **[Message Patterns & Best Practices](https://docs.microsoft.com/azure/architecture/patterns/)**
- **[Azure Functions Service Bus Trigger](https://docs.microsoft.com/azure/azure-functions/functions-bindings-service-bus)**

## 🏷️ Project Metadata

**Technology Stack:**
- ☁️ **Cloud**: Microsoft Azure
- 🚌 **Messaging**: Azure Service Bus
- 🐍 **Language**: Python 3.7+
- 📦 **Dependencies**: azure-servicebus, azure-functions
- 🔐 **Security**: Environment variables, .gitignore
- 🛠️ **Tools**: Azure CLI, pip

**Learning Outcomes:**
- ✅ Azure Service Bus configuration and management
- ✅ Secure credential handling with environment variables  
- ✅ Message producer/consumer patterns
- ✅ Error handling and debugging
- ✅ Azure CLI automation and resource management
