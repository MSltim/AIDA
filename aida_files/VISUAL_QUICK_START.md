
# 🎯 AIDA + Databricks - VISUAL QUICK START

## ⚡ START THE APPLICATION (Choose One Method)

### Method 1: PowerShell Script (EASIEST) ⭐
```powershell
cd C:\AiCOE\AIDA
.\start_aida.ps1
```

### Method 2: Manual Commands
```powershell
cd C:\AiCOE\AIDA
.\AIDA\Scripts\Activate.ps1
python aida.py
```

**What You'll See:**
```
🚀 Starting AIDA Application...
📦 Activating virtual environment...
✅ Virtual environment activated

🌐 Starting Flask server...
   Access the application at: http://localhost:5000

Initializing AIDA workflow with: azure | gpt-4o-ReCast | temp=0.3
AIDA workflow initialized successfully
 * Running on http://127.0.0.1:5000
```

---

## 🌐 OPEN IN BROWSER

Once started, open: **http://localhost:5000**

You'll see the AIDA chat interface:

```
┌─────────────────────────────────────────────────────┐
│  🤖 AIDA - AI Development Assistant                │
│                                                     │
│  ┌──────────────────────────────────────────┐     │
│  │  💬 Chat Messages Appear Here             │     │
│  │                                            │     │
│  │  You: Hi AIDA!                            │     │
│  │  AIDA: Hello! I'm ready to help...       │     │
│  │                                            │     │
│  └──────────────────────────────────────────┘     │
│                                                     │
│  [ Type your message here... ]    [Send] [Upload] │
│                                                     │
│  ⚙️ Settings | 🛠️ Tools | 🤖 Agents              │
└─────────────────────────────────────────────────────┘
```

---

## ✅ ENABLE DATABRICKS (One-Time Setup)

### Step 1: Go to Tools Management
Click **🛠️ Tools** button in the web interface

### Step 2: Find Databricks Tools
Scroll to find:
- ✅ **Databricks Workspace Manager**
- ✅ **Databricks ETL Generator**

### Step 3: Enable Both Tools
Click the **Enable** button next to each

### Step 4: Reload Workflow
Click **Reload Workflow** button at the top

**Result:** ✅ Databricks tools are now active!

---

## 💬 TRY THESE COMMANDS

### Test 1: Check Databricks Connection
**Type in chat:**
```
Show me my Databricks warehouses
```

**AIDA Response:**
```
✅ Found 1 SQL warehouse:

Serverless Starter Warehouse
- ID: 5dc6f8de7e25b32c
- State: RUNNING
- Type: SQL Warehouse
```

### Test 2: List Clusters
**Type in chat:**
```
List all my Databricks clusters
```

**AIDA Response:**
```
You currently have 0 clusters configured.
Would you like me to help you create one?
```

### Test 3: Execute SQL Query
**Type in chat:**
```
Run this query on my SQL warehouse:
SELECT * FROM samples.nyctaxi.trips LIMIT 5
```

**AIDA Response:**
```
Executing on Serverless Starter Warehouse...

Results:
┌──────────────┬──────────────┬────────┬─────────┐
│ trip_distance│ fare_amount  │ vendor │ pickup  │
├──────────────┼──────────────┼────────┼─────────┤
│ 1.50         │ 9.50         │ 2      │ ...     │
│ 2.60         │ 14.00        │ 1      │ ...     │
...
```

### Test 4: Generate ETL Notebook
**Type in chat:**
```
Generate an ETL notebook to transform customer data 
from bronze.customers to silver.customers_clean
```

**AIDA Response:**
```
✅ Generated PySpark ETL notebook

Transformations included:
- Data type casting
- Null handling
- Deduplication
- Email validation

Saved to: customer_bronze_silver_etl.py

You can import this to Databricks Workspace manually.
```

---

## 🏗️ ARCHITECTURE - HOW IT WORKS

```
┌─────────────────────────────────────────────────────────┐
│                      YOUR BROWSER                        │
│                http://localhost:5000                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Request
                     ↓
┌─────────────────────────────────────────────────────────┐
│                    FLASK SERVER                          │
│                     (aida.py)                            │
│                                                          │
│  - Receives chat messages                               │
│  - Manages tools configuration                          │
│  - Handles file uploads                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Routes to appropriate agent
                     ↓
┌─────────────────────────────────────────────────────────┐
│              SUPERVISOR AGENT                           │
│          (Decides which agent to use)                   │
│                                                          │
│  Analyzes request → Routes to specialized agent         │
└──────┬──────────────────────────────────────────────────┘
       │
       ├──→ Software Engineer Agent (code questions)
       ├──→ Data Engineer Agent (Databricks, ETL, SQL) ⭐
       ├──→ Project Manager Agent (Jira, Azure DevOps)
       ├──→ QA Agent (testing questions)
       └──→ General Agent (everything else)
            │
            │ Data Engineer Agent uses:
            ↓
┌─────────────────────────────────────────────────────────┐
│                   MCP TOOLS LAYER                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ 🎯 Databricks Workspace Manager                 │    │
│  │    - List clusters/warehouses                   │    │
│  │    - Execute SQL queries                        │    │
│  │    - Create/list notebooks                      │    │
│  │    - Manage jobs                                │    │
│  │    - Upload files to DBFS                       │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ 🎯 Databricks ETL Generator                     │    │
│  │    - Generate PySpark code                      │    │
│  │    - Create transformation logic                │    │
│  │    - Add error handling & logging               │    │
│  │    - Optimize for performance                   │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  + Atlassian MCP (Jira/Confluence)                     │
│  + Azure DevOps MCP                                     │
│  + Trello MCP                                           │
│  + RAG MCP (Knowledge Base)                             │
│  + SQL MCP (Database)                                   │
│  + Power BI MCP                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Makes API calls
                     ↓
┌─────────────────────────────────────────────────────────┐
│              DATABRICKS WORKSPACE                        │
│      https://dbc-746819f7-4186.cloud.databricks.com    │
│                                                          │
│  - SQL Warehouses                                       │
│  - Notebooks                                             │
│  - Jobs                                                  │
│  - DBFS Storage                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 FILE LOCATIONS - WHERE IS EVERYTHING?

```
C:\AiCOE\AIDA\
│
├── 🚀 START HERE
│   ├── start_aida.ps1          ← Run this to start!
│   ├── aida.py                  ← Main Flask application
│   └── .env                     ← Your credentials
│
├── 📚 DOCUMENTATION
│   ├── QUICK_START.md           ← This file
│   ├── HOW_TO_USE_GUIDE.md     ← Complete guide
│   └── DATABRICKS_USAGE_GUIDE.md
│
├── backend/src/
│   ├── agents/                  ← AI Agents
│   │   ├── supervisor/agent.py  ← Main orchestrator
│   │   └── sub_agent/
│   │       └── DataEngineer/agent.py  ← Uses Databricks
│   │
│   ├── tools/                   ← Integration Layer
│   │   ├── databricks_integration.py  ⭐ Direct Python API
│   │   ├── databricks_tool.py         ⭐ Agent wrapper
│   │   │
│   │   ├── custom_mcp/              ← MCP Servers
│   │   │   ├── Databricks_mcp.py           ⭐ Workspace manager
│   │   │   ├── Databricks_ETL_Generator_mcp.py  ⭐ ETL generator
│   │   │   ├── trello_mcp.py
│   │   │   ├── rag_mcp.py
│   │   │   └── sql_mcp.py
│   │   │
│   │   └── utils/
│   │       ├── mcp_servers.json   📦 All available tools
│   │       └── tools.json         ✅ Currently enabled tools
│   │
│   └── usecase/
│       └── databricks_etl_examples.py  ← Example scripts
│
├── frontend/
│   └── pages/
│       ├── landing.html         ← Main UI
│       └── agent_space.html     ← Agent management
│
└── AIDA/                        ← Virtual environment
    └── Scripts/
        └── python.exe
```

---

## 🔧 HOW TOOLS ARE LOADED

### Step-by-Step Process:

1. **You start AIDA**: `python aida.py`

2. **AIDA reads configuration**:
   ```
   backend/src/tools/utils/tools.json
   ```
   Only tools listed here are loaded!

3. **If tool is enabled**, AIDA loads it:
   - Python scripts: Runs the MCP server
   - Node scripts: Runs via npx
   - Executables: Runs the .exe file

4. **Tools become available** to all agents

### Current Status:

**Available in Catalog** (`mcp_servers.json`):
- ✅ atlassian
- ✅ azure-devops  
- ✅ trello
- ✅ rag
- ✅ sql-mcp
- ✅ powerbi-modeling-mcp
- ✅ **databricks-workspace** ⭐ (NEW!)
- ✅ **databricks-etl** ⭐ (NEW!)

**Currently Enabled** (`tools.json`):
*Check via web UI to see which are active*

---

## 🎯 COMMON USE CASES

### Use Case 1: Data Analysis
```
You: "Connect to Databricks and show top 10 products by revenue"

AIDA:
1. Activates Data Engineer Agent
2. Uses Databricks Workspace Manager tool
3. Lists available warehouses
4. Executes SQL query
5. Returns formatted results
```

### Use Case 2: ETL Development
```
You: "Generate ETL to load CSV files into Delta table"

AIDA:
1. Uses Databricks ETL Generator tool
2. Creates mapping specifications
3. Generates PySpark code with:
   - File reading logic
   - Schema inference
   - Transformations
   - Delta table writing
   - Error handling
4. Saves notebook locally
```

### Use Case 3: Resource Management
```
You: "List all my Databricks resources"

AIDA:
1. Queries clusters
2. Queries SQL warehouses
3. Queries jobs
4. Summarizes in readable format
```

### Use Case 4: Multi-Tool Tasks
```
You: "Query Databricks for customer data, then create a Jira 
ticket to report on findings"

AIDA:
1. Uses Databricks tool to query data
2. Analyzes results
3. Uses Jira tool to create ticket
4. Combines both actions seamlessly
```

---

## 🚨 TROUBLESHOOTING

### Problem: Can't Access http://localhost:5000
**Check:**
1. Is `aida.py` running? (Look for terminal output)
2. Is another app using port 5000? (Try port 5001)
3. Firewall blocking? (Allow Python in firewall)

**Solution:**
```powershell
# Check if port is in use
netstat -ano | findstr :5000

# If blocked, kill the process or use different port
```

### Problem: Databricks Tools Not Showing
**Check:**
1. Did you add to `mcp_servers.json`? ✅ (Already done)
2. Did you enable in web UI? (Do this now)
3. Did you reload workflow? (Click Reload button)

**Solution:**
Refresh browser (Ctrl + F5)

### Problem: SSL Certificate Errors
**Solution:** Already fixed! Your `.env` has:
```
DATABRICKS_SKIP_SSL_VERIFY=true
```

### Problem: 404 Notebook Creation Error
**This is normal!** Workspace permissions issue.

**Workaround:**
1. Generate notebook locally (works ✅)
2. Import manually to Databricks UI
3. OR request admin permissions

---

## ✅ VERIFICATION CHECKLIST

Before using, verify:

- [ ] Virtual environment activated
- [ ] AIDA started: `python aida.py`
- [ ] Browser open: http://localhost:5000
- [ ] Databricks tools added to `mcp_servers.json` ✅
- [ ] Databricks tools enabled in web UI
- [ ] `.env` file has DATABRICKS_HOST and DATABRICKS_TOKEN
- [ ] SSL bypass configured: `DATABRICKS_SKIP_SSL_VERIFY=true`

Test:
- [ ] Ask AIDA: "List my Databricks warehouses"
- [ ] Should return: Serverless Starter Warehouse

---

## 🎓 NEXT STEPS

### Now You Can:

1. **Chat with AIDA** naturally about Databricks
2. **Execute SQL queries** through conversation
3. **Generate ETL notebooks** on demand
4. **Manage clusters** via chat commands
5. **Combine tools** (Databricks + Jira, etc.)

### Try This Workflow:

```
1. Ask: "What Databricks warehouses do I have?"
   → Verify connection works

2. Ask: "Show me sample data from samples.nyctaxi.trips"
   → Test SQL execution

3. Ask: "Generate an ETL notebook for customer data"
   → Test code generation

4. Ask: "Create a Jira ticket to track the ETL deployment"
   → Test multi-tool integration
```

---

## 📞 NEED HELP?

### Quick Commands to Debug:

```powershell
# Test Databricks MCP directly
python backend\src\tools\custom_mcp\test_databricks_mcp.py

# Test integration module
python backend\src\tools\test_integration.py

# Run example use cases
python backend\src\usecase\databricks_etl_examples.py

# Check which tools are enabled
Get-Content backend\src\tools\tools.json
```

### Documentation:
- [QUICK_START.md](QUICK_START.md) ← You are here
- [HOW_TO_USE_GUIDE.md](HOW_TO_USE_GUIDE.md)
- [DATABRICKS_USAGE_GUIDE.md](backend/src/tools/DATABRICKS_USAGE_GUIDE.md)

---

## 🎉 YOU'RE ALL SET!

Run this now:
```powershell
.\start_aida.ps1
```

Then open: **http://localhost:5000**

And ask: **"Show me my Databricks warehouses"**

**Enjoy using AIDA! 🚀**
