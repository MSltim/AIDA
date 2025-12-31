# AIDA Application - Complete Usage Guide

## 📋 Overview
AIDA is a **Flask-based web application** with multi-agent AI capabilities. It uses MCP (Model Context Protocol) tools to extend functionality.

---

## 🚀 How to Start the Application

### Method 1: Run the Flask App (Recommended)
```powershell
# 1. Activate virtual environment
cd C:\AiCOE\AIDA
.\AIDA\Scripts\Activate.ps1

# 2. Run the main application
python aida.py
```

**What happens:**
- Flask server starts on `http://0.0.0.0:5000`
- Opens web interface at `http://localhost:5000`
- Initializes all enabled MCP tools automatically
- Multi-agent workflow becomes available

### Method 2: Access the Web Interface
Once `aida.py` is running, open your browser:
- **Main Page**: http://localhost:5000
- **Agent Space**: http://localhost:5000/agent_space.html

---

## 🛠️ Understanding the Tool System

### Where Are Tools Configured?

#### 1. **All Available Tools** → `backend/src/tools/utils/mcp_servers.json`
This file contains ALL tools that CAN be used. Think of it as the "tool catalog".

**Current tools:**
- ✅ Atlassian (Jira/Confluence)
- ✅ Azure DevOps
- ✅ Trello
- ✅ RAG (Knowledge Base)
- ✅ SQL Database
- ✅ Power BI Modeling
- ❌ **Databricks** (missing - we'll add it)

#### 2. **Enabled Tools** → `backend/src/tools/tools.json`
This file contains only the tools that are CURRENTLY ACTIVE in AIDA.

**How it works:**
- When you start `aida.py`, it only loads tools from `tools.json`
- You can enable/disable tools via the web UI (Tools Management page)
- When you toggle a tool, it copies config from `mcp_servers.json` → `tools.json`

---

## 📊 Adding Databricks to Your Application

### Step 1: Add Databricks to the Tool Catalog
We need to add Databricks to `mcp_servers.json`:

```json
{
  "databricks-workspace": {
    "name": "Databricks Workspace Manager",
    "description": "Manage Databricks clusters, notebooks, SQL queries, and DBFS. Requires DATABRICKS_HOST and DATABRICKS_TOKEN in .env",
    "script": "tools/custom_mcp/Databricks_mcp.py",
    "enabled": true
  },
  "databricks-etl": {
    "name": "Databricks ETL Generator",
    "description": "Generate production-ready ETL notebooks from mapping specifications. Creates PySpark code for data transformations.",
    "script": "tools/custom_mcp/Databricks_ETL_Generator_mcp.py",
    "enabled": true
  }
}
```

### Step 2: Enable in Web UI
1. Start `python aida.py`
2. Go to http://localhost:5000
3. Navigate to **Tools Management** section
4. Find **Databricks Workspace Manager** and click **Enable**
5. Find **Databricks ETL Generator** and click **Enable**
6. Click **Reload Workflow** to apply changes

---

## 💡 How to Use Databricks Integration

### Option A: Through AIDA Web Chat
Once Databricks tools are enabled, you can ask AIDA:

```
"List all my Databricks clusters"
"Show me available SQL warehouses"
"Execute this query on warehouse: SELECT * FROM catalog.schema.table LIMIT 10"
"Generate an ETL notebook to move data from source_table to target_table"
```

AIDA's agents will automatically use the Databricks tools to fulfill your requests.

### Option B: Direct Python Integration (Programmatic)
Use the integration module in your custom agents/scripts:

```python
from backend.src.tools.databricks_integration import get_databricks_manager

# Get singleton instance
db = get_databricks_manager()

# List resources
clusters = db.list_clusters()
warehouses = db.list_warehouses()

# Execute SQL
result = db.execute_sql(
    warehouse_id="your_warehouse_id",
    query="SELECT * FROM catalog.schema.table LIMIT 10"
)

# Generate ETL notebook
etl_code = db.generate_etl_notebook([
    {
        "mapping_name": "customer_mapping",
        "mapping_complexity": "simple",
        "source_name": "source_db",
        "target_name": "target_db",
        "source_type": "table",
        "target_type": "table",
        "source_object": "customers",
        "source_field": "customer_id",
        "transformation_logic": "direct_copy",
        "target_object": "customers_transformed",
        "target_field": "id"
    }
])
```

### Option C: Create Custom Agents
See example in `backend/src/agents/sub_agent/DataEngineer/agent.py`:

```python
from backend.src.tools.databricks_tool import create_databricks_tools

# In your agent setup
databricks_tools = create_databricks_tools()
agent = Agent(tools=databricks_tools, ...)
```

---

## 📁 Application Structure Explained

```
C:\AiCOE\AIDA\
│
├── aida.py                          # ⭐ MAIN APPLICATION (Flask server)
│   └── Runs on http://localhost:5000
│
├── frontend/                        # Web UI files
│   └── pages/
│       ├── landing.html            # Main chat interface
│       └── agent_space.html        # Agent management
│
├── backend/src/
│   ├── agents/                     # AI agents
│   │   └── supervisor/agent.py     # Main orchestrator
│   │
│   ├── tools/                      # MCP Tools
│   │   ├── databricks_integration.py    # ⭐ Direct Python API
│   │   ├── databricks_tool.py          # Agent wrapper
│   │   │
│   │   ├── custom_mcp/                 # Custom MCP servers
│   │   │   ├── Databricks_mcp.py      # Workspace manager
│   │   │   ├── Databricks_ETL_Generator_mcp.py  # ETL generator
│   │   │   ├── trello_mcp.py
│   │   │   ├── rag_mcp.py
│   │   │   └── sql_mcp.py
│   │   │
│   │   └── utils/
│   │       ├── mcp_servers.json    # 📦 All available tools
│   │       └── tools.json          # ✅ Currently enabled tools
│   │
│   └── usecase/
│       └── databricks_etl_examples.py  # Example usage scripts
│
├── .env                            # Environment variables
│   ├── DATABRICKS_HOST=...
│   ├── DATABRICKS_TOKEN=...
│   └── DATABRICKS_SKIP_SSL_VERIFY=true
│
└── AIDA/                           # Virtual environment
    └── Scripts/
        └── python.exe
```

---

## 🔄 Complete Workflow

### 1. Starting AIDA
```powershell
cd C:\AiCOE\AIDA
.\AIDA\Scripts\Activate.ps1
python aida.py
```

**Output you'll see:**
```
Initializing AIDA workflow with: azure | gpt-4o-ReCast | temp=0.3
AIDA workflow initialized successfully
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### 2. Using the Web Interface
- Open browser → http://localhost:5000
- Chat with AIDA using natural language
- Upload documents for RAG processing
- Manage tools (enable/disable)
- Switch AI models (Azure OpenAI / Google Gemini)

### 3. What Happens Behind the Scenes
```
User Message
    ↓
Flask API (/api/chat)
    ↓
Supervisor Agent (decides which sub-agent to use)
    ↓
Sub-Agent (DataEngineer, SoftwareEngineer, etc.)
    ↓
MCP Tools (Databricks, Jira, SQL, etc.)
    ↓
Response back to user
```

---

## 🧪 Testing Databricks Integration

### Quick Test
```powershell
# Test MCP servers directly
python backend\src\tools\custom_mcp\test_databricks_mcp.py

# Test integration module
python backend\src\tools\test_integration.py

# Run complete examples
python backend\src\usecase\databricks_etl_examples.py
```

### Verify in AIDA Web UI
1. Start AIDA: `python aida.py`
2. Go to http://localhost:5000
3. Ask: "What Databricks warehouses do I have?"
4. AIDA should respond with warehouse information

---

## 🎯 Common Use Cases

### Use Case 1: Data Analysis
**Ask AIDA:**
> "Connect to my Databricks warehouse and show me the top 10 customers by revenue"

**What happens:**
1. AIDA's DataEngineer agent activates
2. Uses `databricks-workspace` tool
3. Lists warehouses → selects one
4. Executes SQL query
5. Returns results formatted in chat

### Use Case 2: ETL Generation
**Ask AIDA:**
> "Generate an ETL notebook to transform customer data from bronze to silver layer"

**What happens:**
1. AIDA uses `databricks-etl` tool
2. Creates mapping specifications
3. Generates PySpark code
4. Saves locally or deploys to workspace (if permissions allow)

### Use Case 3: Cluster Management
**Ask AIDA:**
> "Start my development cluster and run this analysis"

**What happens:**
1. Lists clusters using Databricks MCP
2. Starts specified cluster
3. Waits for RUNNING state
4. Executes your analysis

---

## 🚨 Troubleshooting

### Problem: "Can't find aida.py"
**Solution:** You ARE using aida.py correctly! It's Flask, not Streamlit.
- There's no Streamlit in this application
- Run: `python aida.py` (not streamlit run)

### Problem: "Databricks tools not showing in AIDA"
**Solution:**
1. Check `mcp_servers.json` contains Databricks entries
2. Enable via web UI or manually add to `tools.json`
3. Reload workflow: POST to `/api/tools/reload`

### Problem: "SSL Certificate Error"
**Solution:** Already configured in your `.env`:
```
DATABRICKS_SKIP_SSL_VERIFY=true
```

### Problem: "404 when creating notebooks"
**Solution:** This is a workspace permission issue:
- Generate notebooks locally (already working)
- Manually import to Databricks UI
- OR request permissions from Databricks admin

---

## 📝 Summary

| Action | Command |
|--------|---------|
| Start AIDA | `python aida.py` |
| Access Web UI | http://localhost:5000 |
| Test Databricks | `python backend\src\tools\test_integration.py` |
| View enabled tools | Check `backend/src/tools/tools.json` |
| Add new tool | Edit `backend/src/tools/utils/mcp_servers.json` |
| Direct Python usage | `from backend.src.tools.databricks_integration import get_databricks_manager` |

**Key Points:**
- ✅ AIDA is Flask-based (NOT Streamlit)
- ✅ Tools are loaded dynamically from `tools.json`
- ✅ Databricks integration works via MCP or direct Python API
- ✅ All SSL issues resolved with environment variable
- ✅ Web UI provides chat interface for natural language interaction

---

## 🎓 Next Steps

1. **Add Databricks to tool catalog** (I'll do this next)
2. **Start AIDA**: `python aida.py`
3. **Enable Databricks** via web UI
4. **Ask AIDA** to use Databricks features
5. **Build custom agents** using the integration examples

Need help with any of these steps? Just ask! 🚀
