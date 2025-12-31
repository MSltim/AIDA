# 🚀 Databricks Integration - Quick Usage Guide

## Where to Use the Databricks Integration

The `databricks_integration.py` module can be used in various parts of your AIDA application:

---

## 1️⃣ **In Agents** (Recommended)
**Location:** `backend/src/agents/sub_agent/[AgentName]/agent.py`

### Example: DataEngineer Agent
```python
from backend.src.tools.databricks_integration import get_databricks_manager

async def DataEngineeringAgent(provider, model_name, temperature, tools=None):
    db = get_databricks_manager()
    
    # Add Databricks tools to your agent
    @tool
    def list_clusters():
        """List Databricks clusters"""
        return db.list_clusters()
    
    # Create agent with Databricks tools
    agent = create_react_agent(llm, tools=[list_clusters, ...])
    return agent
```

**Files:**
- ✅ `backend/src/agents/sub_agent/DataEngineer/agent.py` (Created)
- ✅ `backend/src/tools/databricks_tool.py` (Created)

---

## 2️⃣ **In Use Cases**
**Location:** `backend/src/usecase/`

### Example: Standalone ETL Script
```python
from backend.src.tools.databricks_integration import get_databricks_manager

def generate_customer_etl():
    db = get_databricks_manager()
    
    # Define mappings
    mappings = [
        {"source_field": "id", "target_field": "customer_id"},
        # ... more mappings
    ]
    
    # Generate ETL
    result = db.generate_etl_notebook(
        mappings=mappings,
        source_objects=[...],
        target_objects=[...]
    )
    
    return result
```

**Files:**
- ✅ `backend/src/usecase/databricks_etl_examples.py` (Created)

---

## 3️⃣ **In API Endpoints** (if using FastAPI)
**Location:** `aida.py` or new API routes

### Example: FastAPI Endpoint
```python
from fastapi import APIRouter
from backend.src.tools.databricks_integration import get_databricks_manager

router = APIRouter(prefix="/databricks", tags=["databricks"])
db = get_databricks_manager()

@router.get("/clusters")
async def list_clusters():
    """List all Databricks clusters"""
    return db.list_clusters()

@router.post("/notebook")
async def create_notebook(path: str, content: str):
    """Create a Databricks notebook"""
    return db.create_notebook(path, content)
```

---

## 4️⃣ **In Utility Scripts**
**Location:** `backend/src/utils/` or standalone scripts

### Example: Data Pipeline Utility
```python
from backend.src.tools.databricks_integration import get_databricks_manager

class DataPipelineManager:
    def __init__(self):
        self.db = get_databricks_manager()
    
    def deploy_pipeline(self, pipeline_config):
        # Generate notebooks
        etl_result = self.db.generate_etl_notebook(...)
        
        # Deploy to Databricks
        notebook_result = self.db.create_notebook(...)
        
        return {"etl": etl_result, "notebook": notebook_result}
```

---

## 📋 **Complete Usage Examples**

### Example 1: List Resources
```python
from backend.src.tools.databricks_integration import get_databricks_manager

db = get_databricks_manager()

# List clusters
result = db.list_clusters()
if result['success']:
    for cluster in result['data']['clusters']:
        print(f"{cluster['cluster_name']}: {cluster['state']}")

# List warehouses
result = db.list_warehouses()
if result['success']:
    for wh in result['data']['warehouses']:
        print(f"{wh['name']}: {wh['state']}")
```

### Example 2: Create Notebook
```python
from backend.src.tools.databricks_integration import get_databricks_manager

db = get_databricks_manager()

notebook_code = '''
# Data Analysis Notebook
from pyspark.sql.functions import *

df = spark.read.format("delta").load("/data/sales")
df.groupBy("product").sum("revenue").show()
'''

result = db.create_notebook(
    path="/Users/data_team/analysis",
    content=notebook_code,
    language="PYTHON"
)

print(result)
```

### Example 3: Generate ETL
```python
from backend.src.tools.databricks_integration import get_databricks_manager

db = get_databricks_manager()

mappings = [
    {
        "source_object": "customers_csv",
        "source_field": "customer_id",
        "target_object": "customer_dim",
        "target_field": "id"
    },
    {
        "source_object": "customers_csv",
        "source_field": "name",
        "target_object": "customer_dim",
        "target_field": "customer_name",
        "transformation": "uppercase"
    }
]

source_objects = [{
    "name": "customers_csv",
    "type": "csv",
    "path": "/data/customers.csv"
}]

target_objects = [{
    "name": "customer_dim",
    "type": "delta",
    "path": "/delta/customer_dim",
    "mode": "overwrite"
}]

result = db.generate_etl_notebook(
    mappings=mappings,
    source_objects=source_objects,
    target_objects=target_objects,
    notebook_name="Customer_ETL"
)

if result['success']:
    print(f"Generated {len(result['notebook_code'])} characters of code")
    # Save to file
    with open("customer_etl.py", "w") as f:
        f.write(result['notebook_code'])
```

### Example 4: Execute SQL
```python
from backend.src.tools.databricks_integration import get_databricks_manager

db = get_databricks_manager()

# Get warehouse
warehouses = db.list_warehouses()
warehouse_id = warehouses['data']['warehouses'][0]['id']

# Execute query
result = db.execute_sql(
    warehouse_id=warehouse_id,
    query="SELECT COUNT(*) as total FROM my_table"
)

print(result)
```

---

## 🎯 **Testing Your Integration**

### Run Examples
```bash
# Test integration module
cd C:\AiCOE\AIDA
.\AIDA\Scripts\python.exe backend\src\tools\test_integration.py

# Run use case examples
.\AIDA\Scripts\python.exe backend\src\usecase\databricks_etl_examples.py

# Test MCP server
.\AIDA\Scripts\python.exe backend\src\tools\custom_mcp\test_databricks_mcp.py
```

---

## 📂 **File Structure Summary**

```
C:\AiCOE\AIDA\
├── backend\src\
│   ├── tools\
│   │   ├── databricks_integration.py  ✅ Main integration module
│   │   ├── databricks_tool.py         ✅ Tool wrapper for agents
│   │   ├── test_integration.py        ✅ Test script
│   │   └── custom_mcp\
│   │       ├── Databricks_mcp.py      ✅ MCP server (updated)
│   │       └── Databricks_ETL_Generator_mcp.py  ✅ ETL MCP (updated)
│   │
│   ├── agents\sub_agent\
│   │   └── DataEngineer\
│   │       └── agent.py               ✅ Example agent
│   │
│   └── usecase\
│       └── databricks_etl_examples.py ✅ Example use cases
│
└── .env                                ✅ Contains DATABRICKS_HOST, DATABRICKS_TOKEN
```

---

## 🚀 **Next Steps**

1. **Test the examples:**
   ```bash
   python backend\src\usecase\databricks_etl_examples.py
   ```

2. **Integrate into your agent:**
   - Copy patterns from `DataEngineer/agent.py`
   - Add Databricks tools to existing agents

3. **Create your own use cases:**
   - Use `databricks_etl_examples.py` as template
   - Build custom ETL pipelines

4. **Use in API:**
   - Add Databricks endpoints to `aida.py`
   - Expose operations via REST API

---

## 💡 **Tips**

- ✅ All tests passing? Start using in your code!
- 🔒 SSL bypass is configured for corporate proxy
- 📝 Check logs if operations fail
- 🔧 Extend `DatabricksManager` class for custom operations
- 🎯 Use `get_databricks_manager()` - it's a singleton

---

**Ready to use!** 🎉
