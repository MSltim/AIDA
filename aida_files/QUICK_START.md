# 🚀 AIDA - Quick Start Guide

## Start the Application (3 Simple Steps)

### Method 1: Using PowerShell Script (Easiest)
```powershell
cd C:\AiCOE\AIDA
.\start_aida.ps1
```

### Method 2: Manual Start
```powershell
cd C:\AiCOE\AIDA
.\AIDA\Scripts\Activate.ps1
python aida.py
```

## Access the Application
Once started, open your browser:
- **Main Chat Interface**: http://localhost:5000
- **Agent Space**: http://localhost:5000/agent_space.html

---

## ✨ What Can AIDA Do?

### 1. Chat with AI Agents
Ask natural language questions and AIDA will route to the right agent:
- Software engineering questions
- Data analysis and ETL
- Project management via Jira/Azure DevOps
- SQL database queries
- Knowledge base (RAG) queries

### 2. Databricks Integration (NEW! ✅)
Now enabled in AIDA! Ask things like:
- "List my Databricks clusters"
- "Show available SQL warehouses"
- "Execute this query: SELECT * FROM my_table LIMIT 10"
- "Generate an ETL notebook to transform customer data"

### 3. Upload Documents
- Drag & drop files into the chat
- Automatically vectorized for RAG
- Ask questions about uploaded documents

### 4. Manage Tools
- Enable/disable MCP tools dynamically
- Switch between AI models (Azure OpenAI, Google Gemini)
- Adjust temperature and other settings

---

## 🛠️ Databricks Setup Status

✅ **Databricks Integration Installed**
- Location: `backend/src/tools/databricks_integration.py`
- MCP Servers: `Databricks_mcp.py` and `Databricks_ETL_Generator_mcp.py`
- Configuration: Credentials in `.env` file
- SSL Issues: ✅ Resolved with `DATABRICKS_SKIP_SSL_VERIFY=true`

✅ **Added to Tool Catalog**
- Check: `backend/src/tools/utils/mcp_servers.json`
- Two tools available:
  1. **Databricks Workspace Manager** - Clusters, notebooks, SQL, jobs
  2. **Databricks ETL Generator** - Generate PySpark ETL code

### Enable Databricks in AIDA
**Option A: Via Web UI (Recommended)**
1. Start AIDA: `.\start_aida.ps1`
2. Open: http://localhost:5000
3. Navigate to **Tools Management**
4. Find **Databricks Workspace Manager** → Click **Enable**
5. Find **Databricks ETL Generator** → Click **Enable**
6. Click **Reload Workflow**

**Option B: Manual (Advanced)**
Copy the Databricks entries from `mcp_servers.json` to `tools.json`:
```bash
# This will be done automatically via web UI
```

---

## 💬 Example Conversations

### Example 1: List Resources
**You:** "What Databricks resources do I have?"

**AIDA:** 
```
I found 1 SQL warehouse:
- Serverless Starter Warehouse (ID: 5dc6f8de7e25b32c)
  Status: RUNNING
  
You currently have 0 clusters configured.
```

### Example 2: Execute SQL
**You:** "Run this query on my warehouse: SELECT * FROM samples.nyctaxi.trips LIMIT 5"

**AIDA:** 
```
Executing query on Serverless Starter Warehouse...

Results:
[Shows first 5 rows of NYC taxi data]
```

### Example 3: Generate ETL
**You:** "Create an ETL notebook to move customer data from bronze to silver layer"

**AIDA:** 
```
Generated ETL notebook with:
- Source: bronze.customers
- Target: silver.customers_clean
- Transformations: data cleaning, deduplication, type casting

Notebook saved to: customer_bronze_to_silver_etl.py
You can import this to Databricks workspace manually.
```

---

## 📊 Architecture Overview

```
Browser (http://localhost:5000)
    ↓
Flask Server (aida.py)
    ↓
Supervisor Agent
    ↓ ↓ ↓ ↓ ↓
    ├── Software Engineer Agent
    ├── Data Engineer Agent ← Uses Databricks tools
    ├── Project Manager Agent  
    ├── QA Agent
    └── General Agent
    ↓
MCP Tools Layer
    ├── Databricks Workspace Manager ← NEW!
    ├── Databricks ETL Generator ← NEW!
    ├── Atlassian (Jira/Confluence)
    ├── Azure DevOps
    ├── Trello
    ├── RAG (Knowledge Base)
    ├── SQL Database
    └── Power BI
```

---

## 🧪 Testing Databricks

### Quick Health Check
```powershell
# Test MCP server directly
python backend\src\tools\custom_mcp\test_databricks_mcp.py

# Test integration module
python backend\src\tools\test_integration.py

# Run usage examples
python backend\src\usecase\databricks_etl_examples.py
```

Expected output: ✅ 5/5 tests passed

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [HOW_TO_USE_GUIDE.md](HOW_TO_USE_GUIDE.md) | Complete usage guide (you are here) |
| [DATABRICKS_USAGE_GUIDE.md](backend/src/tools/DATABRICKS_USAGE_GUIDE.md) | Databricks-specific API reference |
| [DATABRICKS_INTEGRATION_SUMMARY.md](DATABRICKS_INTEGRATION_SUMMARY.md) | Implementation summary |
| [SETUP_CHECKLIST.md](backend/src/tools/custom_mcp/SETUP_CHECKLIST.md) | Original setup instructions |

---

## 🎯 Common Tasks

### Start AIDA
```powershell
.\start_aida.ps1
```

### Stop AIDA
Press `Ctrl + C` in the terminal

### Check Enabled Tools
1. Open http://localhost:5000
2. Go to Tools Management section
3. See which tools have green checkmarks

### View Logs
Logs appear in the terminal where you ran `aida.py`:
```
Initializing AIDA workflow...
AIDA workflow initialized successfully
Loading MCP tools...
✅ databricks-workspace loaded
✅ databricks-etl loaded
```

### Update .env Configuration
Edit `C:\AiCOE\AIDA\.env`:
```env
# Databricks
DATABRICKS_HOST="https://dbc-746819f7-4186.cloud.databricks.com"
DATABRICKS_TOKEN="your_token_here"
DATABRICKS_SKIP_SSL_VERIFY=true

# Azure OpenAI
AZURE_OPENAI_ENDPOINT="..."
AZURE_OPENAI_API_KEY="..."

# Google (optional)
GOOGLE_API_KEY="..."
```

---

## 🚨 Troubleshooting

### Issue: "Port 5000 already in use"
**Solution:** Stop the existing process or use a different port:
```python
# Edit aida.py, line 376
app.run(debug=False, host='0.0.0.0', port=5001, threaded=True)
```

### Issue: "Module not found" errors
**Solution:** Reinstall dependencies:
```powershell
.\AIDA\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Can't see Databricks in UI"
**Solution:** 
1. Check `mcp_servers.json` includes databricks entries ✅ (Already added)
2. Reload the page (Ctrl + F5)
3. Check browser console for errors (F12)

### Issue: "SSL Certificate Error"
**Solution:** Already configured! Check `.env` has:
```
DATABRICKS_SKIP_SSL_VERIFY=true
```

---

## ⚡ Pro Tips

1. **Use Natural Language**: Don't worry about exact syntax, just ask naturally
2. **Upload Context**: Upload relevant documents before asking questions
3. **Chain Requests**: AIDA can handle multi-step tasks
4. **Switch Models**: Try different AI models for different tasks
5. **Enable Only What You Need**: Disable unused tools for faster response

---

## 🎓 Next Steps

1. ✅ Start AIDA: `.\start_aida.ps1`
2. ✅ Enable Databricks tools via web UI
3. ✅ Test with simple query: "List my Databricks warehouses"
4. ✅ Try ETL generation: "Generate ETL for customer data"
5. ✅ Build custom agents using the integration examples

---

**🎉 You're Ready to Go!**

Run `.\start_aida.ps1` and start chatting with AIDA at http://localhost:5000
