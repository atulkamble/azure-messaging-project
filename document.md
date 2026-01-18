# 📩 Azure Messaging Project – Service Bus + Python + Streamlit

## 📌 Overview

This project demonstrates how to use **Azure Service Bus Queues** with **Python** and a **Streamlit UI** to send messages to a queue.

You will:

* Create an Azure Service Bus
* Configure connection settings locally
* Create a queue
* Send messages using Python
* Visualize / interact using Streamlit

---

## ✅ Prerequisites

Make sure the following are installed on your system:

* **Python 3.x**
* **pip**
* **Git**
* **VS Code**
* **Azure Subscription**

Verify installation:

```bash
python --version
pip --version
git --version
```

---

## 📂 Step 1: Clone the Project

```bash
git clone https://github.com/atulkamble/azure-messaging-project.git
cd azure-messaging-project
git pull
```

---

## ▶️ Step 2: Run the Application (Initial Test)

```bash
streamlit run app.py
```

> This verifies that Streamlit and dependencies are working correctly.

---

## 🧑‍💻 Step 3: Open Project in VS Code

```bash
code .
```

---

## ☁️ Step 4: Create Azure Service Bus

1. Login to **Azure Portal**
2. Create **Service Bus**
3. Choose:

   * Pricing Tier: **Basic / Standard**
   * **Namespace name must be globally unique**

---

## 🔐 Step 5: Get Service Bus Connection String

Navigate to:

```
Service Bus Namespace
→ Shared access policies
→ RootManageSharedAccessKey
```

Copy the **Primary Connection String**

### Example:

```text
Endpoint=sb://atulkamble.servicebus.windows.net/;
SharedAccessKeyName=RootManageSharedAccessKey;
SharedAccessKey=boDzYKmErppMsAIjYHkDV3G0jnyWJFdsc+ASbNSyxWI=
```

---

## ⚙️ Step 6: Update `local.settings.json`

Open `local.settings.json` and replace the connection string:

```json
{
  "SERVICE_BUS_CONNECTION_STRING": "PASTE_YOUR_CONNECTION_STRING_HERE"
}
```

⚠️ **Do not commit real connection strings to GitHub**

---

## 📦 Step 7: Create Service Bus Queue

In Azure Portal:

```
Service Bus Namespace
→ Queues
→ + Queue
```

* **Queue Name:** `orders-queue`

---

## 📤 Step 8: Send Message to Queue

Run the Python producer script:

```bash
python send_message.py
```

✔️ This sends a message to the `orders-queue`

---

## 🖥️ Step 9: Run Streamlit UI

```bash
streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

You can now interact with the Azure Service Bus–backed application.

---

## 📁 Project Flow Summary

```
Streamlit UI
   ↓
Python App
   ↓
Azure Service Bus Queue (orders-queue)
```

---

## 🧪 Common Issues & Fixes

| Issue               | Solution                        |
| ------------------- | ------------------------------- |
| Streamlit not found | `pip install streamlit`         |
| Queue not found     | Verify queue name exactly       |
| Connection error    | Recheck connection string       |
| Permission denied   | Use `RootManageSharedAccessKey` |

---

## 🔒 Security Best Practices

* Use **Azure Key Vault** instead of plain JSON files for production
* Rotate Service Bus keys regularly
* Avoid committing secrets to GitHub

---

## 📌 Use Cases

* Order processing systems
* Event-driven microservices
* Decoupled producer–consumer architecture
* Azure messaging demos & training

---
