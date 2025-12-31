# 🚀 Databricks MCP - Quick Setup Checklist

Use this checklist to get your Databricks MCP tools up and running in minutes!

---

## ✅ Prerequisites (2 minutes)

- [ ] You have access to a Databricks workspace
- [ ] You can log into the Databricks UI
- [ ] You have Python 3.8+ installed
- [ ] VS Code is installed with the appropriate extensions

---

## ✅ Step 1: Get Databricks Credentials (3 minutes)

### Get Workspace URL
- [ ] Log into Databricks
- [ ] Copy URL from browser address bar
      Example: `https://adb-1234567890123456.7.azuredatabricks.net`
- [ ] Save this URL for later

### Generate Access Token
- [ ] Click your profile icon (top-right)
- [ ] Select **User Settings**
- [ ] Go to **Access Tokens** tab
- [ ] Click **Generate New Token**
- [ ] Give it a name: "MCP Server Token"
- [ ] Set expiration (or leave blank)
- [ ] Click **Generate**
- [ ] ⚠️ **COPY TOKEN NOW** (you won't see it again!)
- [ ] Save token securely

**Got Both?** ✅ Workspace URL ✅ Access Token

---

## ✅ Step 2: Configure Environment (2 minutes)

### Update .env File
- [ ] Open: `C:\AiCOE\AIDA\.env`
- [ ] Add these lines:

```env
DATABRICKS_HOST=https://your-workspace-url-here
DATABRICKS_TOKEN=<databricks_api_token>
```

- [ ] Replace with your actual values
- [ ] Save the file

**Example:**
```env
DATABRICKS_HOST=https://adb-1234567890123456.7.azuredatabricks.net
DATABRICKS_TOKEN=d<databricks_api_token>
```

---

## ✅ Step 3: Install Dependencies (1 minute)

### Activate Virtual Environment
```powershell
cd C:\AiCOE\AIDA
& .\AIDA\Scripts\Activate.ps1
```

- [ ] Virtual environment activated (you see `(AIDA)` in prompt)

### Install Packages
```powershell
pip install python-dotenv mcp requests
```

- [ ] Installation completed successfully

---

## ✅ Step 4: Test Connection (1 minute)

### Run Test Script
```powershell
python backend\src\tools\custom_mcp\test_databricks_mcp.py
```

### Expected Results:
- [ ] ✅ Environment variables found
- [ ] ✅ Python packages installed
- [ ] ✅ Databricks connection successful
- [ ] ✅ Can list clusters
- [ ] ✅ Can list warehouses

**All tests passed?** → Continue to Step 5

**Tests failed?** → Check:
- [ ] Workspace URL is correct (includes https://)
- [ ] Token is valid and not expired
- [ ] No extra spaces in .env file
- [ ] Virtual environment is activated

---

## ✅ Step 5: Choose Integration Method (1 minute)

### Identify Your AI Assistant

First, check which AI assistant you're using:

```powershell
code --list-extensions | Select-String -Pattern "copilot|claude|cline"
```

**Results:**
- **`github.copilot`** → Use **Method A: Direct Integration** (recommended)
- **`saoudrizwan.claude-dev` or `cline`** → Use **Method B: MCP Server Configuration**

---

## ✅ Method A: Direct Integration (For GitHub Copilot Users) - 5 minutes

### Step 5A-1: Create Integration Module

```powershell
# Create the integration file
New-Item -Path "backend\src\tools\databricks_integration.py" -ItemType File -Force
```

### Step 5A-2: Add Integration Code

- [ ] Open `backend\src\tools\databricks_integration.py`
- [ ] Copy and paste the following code:

```python
"""
Databricks Integration for AIDA
Provides direct access to Databricks MCP tools
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add custom_mcp directory to Python path
CUSTOM_MCP_PATH = Path(__file__).parent / "custom_mcp"
if str(CUSTOM_MCP_PATH) not in sys.path:
    sys.path.insert(0, str(CUSTOM_MCP_PATH))

# Import Databricks modules
try:
    import Databricks_mcp as db_mcp
    import Databricks_ETL_Generator_mcp as etl_mcp
    DATABRICKS_AVAILABLE = True
except ImportError as e:
    DATABRICKS_AVAILABLE = False
    print(f"Warning: Databricks modules not available: {e}")


class DatabricksManager:
    """Central manager for all Databricks operations"""
    
    def __init__(self):
        if not DATABRICKS_AVAILABLE:
            raise RuntimeError("Databricks modules are not available")
    
    # Cluster Management
    def list_clusters(self) -> List[Dict]:
        """List all Databricks clusters"""
        return db_mcp.list_clusters()
    
    def get_cluster_info(self, cluster_id: str) -> Dict:
        """Get detailed info about a specific cluster"""
        return db_mcp.get_cluster_info(cluster_id)
    
    def start_cluster(self, cluster_id: str) -> Dict:
        """Start a cluster"""
        return db_mcp.start_cluster(cluster_id)
    
    def terminate_cluster(self, cluster_id: str) -> Dict:
        """Terminate a cluster"""
        return db_mcp.terminate_cluster(cluster_id)
    
    # Warehouse Management
    def list_warehouses(self) -> List[Dict]:
        """List all SQL warehouses"""
        return db_mcp.list_warehouses()
    
    def get_warehouse_info(self, warehouse_id: str) -> Dict:
        """Get warehouse details"""
        return db_mcp.get_warehouse_info(warehouse_id)
    
    # Notebook Operations
    def create_notebook(self, path: str, content: str, language: str = "PYTHON") -> Dict:
        """Create a new notebook"""
        return db_mcp.create_notebook(path, content, language)
    
    def read_notebook(self, path: str) -> Dict:
        """Read notebook content"""
        return db_mcp.read_notebook(path)
    
    def list_notebooks(self, path: str = "/") -> List[Dict]:
        """List notebooks in a directory"""
        return db_mcp.list_notebooks(path)
    
    # SQL Query Execution
    def execute_sql(self, warehouse_id: str, query: str) -> Dict:
        """Execute SQL query on a warehouse"""
        return db_mcp.execute_sql(warehouse_id, query)
    
    # ETL Generation
    def generate_etl_notebook(self, mappings: Dict[str, Any]) -> str:
        """Generate ETL notebook from mappings"""
        return etl_mcp.generate_etl_notebook(mappings)
    
    def validate_mappings(self, mappings: Dict[str, Any]) -> Dict:
        """Validate ETL mappings"""
        return etl_mcp.validate_mappings(mappings)


# Singleton instance
_databricks_manager = None

def get_databricks_manager() -> DatabricksManager:
    """Get or create the Databricks manager singleton"""
    global _databricks_manager
    if _databricks_manager is None:
        _databricks_manager = DatabricksManager()
    return _databricks_manager
```

- [ ] Save the file

### Step 5A-3: Test Integration

```powershell
python -c "from backend.src.tools.databricks_integration import get_databricks_manager; dm = get_databricks_manager(); print('✅ Integration loaded successfully')"
```

### Step 5A-4: Use in Your Code

Now you can use Databricks anywhere in AIDA:

```python
from backend.src.tools.databricks_integration import get_databricks_manager

# Get manager instance
db = get_databricks_manager()

# List clusters
clusters = db.list_clusters()
print(f"Found {len(clusters)} clusters")

# Create notebook
result = db.create_notebook(
    path="/Users/me/my_notebook",
    content="# My Notebook\nprint('Hello Databricks')",
    language="PYTHON"
)

# Generate ETL
etl_code = db.generate_etl_notebook({
    "source": {...},
    "target": {...},
    "mappings": [...]
})
```

**✅ Done!** Skip to [Step 6: Test Integration](#step-6-test-integration-github-copilot)

---

## ✅ Method B: MCP Server Configuration (For Claude-dev/Cline Users) - 3 minutes

### Step 5B-1: Find MCP Config File

**Windows Path:**
```
%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

**Or navigate:**
- [ ] Press `Win+R`
- [ ] Type: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings`
- [ ] Open `cline_mcp_settings.json`

### Step 5B-2: Add Databricks Servers

**If file is empty or has `{}`:**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "C:\\AiCOE\\AIDA\\AIDA\\Scripts\\python.exe",
      "args": [
        "C:\\AiCOE\\AIDA\\backend\\src\\tools\\custom_mcp\\Databricks_mcp.py"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-actual-token-here"
      }
    },
    "databricks-etl": {
      "command": "C:\\AiCOE\\AIDA\\AIDA\\Scripts\\python.exe",
      "args": [
        "C:\\AiCOE\\AIDA\\backend\\src\\tools\\custom_mcp\\Databricks_ETL_Generator_mcp.py"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-actual-token-here"
      }
    }
  }
}
```

**If file already has other servers (like Jira):**
```json
{
  "mcpServers": {
    "jira": {
      // ... existing jira config ...
    },
    "databricks": {
      "command": "C:\\AiCOE\\AIDA\\AIDA\\Scripts\\python.exe",
      "args": [
        "C:\\AiCOE\\AIDA\\backend\\src\\tools\\custom_mcp\\Databricks_mcp.py"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-actual-token-here"
      }
    },
    "databricks-etl": {
      "command": "C:\\AiCOE\\AIDA\\AIDA\\Scripts\\python.exe",
      "args": [
        "C:\\AiCOE\\AIDA\\backend\\src\\tools\\custom_mcp\\Databricks_ETL_Generator_mcp.py"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-actual-token-here"
      }
    }
  }
}
```

**Important:**
- [ ] Replace `your-workspace.cloud.databricks.com` with your actual URL
- [ ] Replace `your-actual-token-here` with your actual token
- [ ] Use double backslashes `\\` in Windows paths
- [ ] Ensure proper JSON syntax (commas, quotes)

### Step 5B-3: Verify Paths
- [ ] Python path exists: `C:\AiCOE\AIDA\AIDA\Scripts\python.exe`
- [ ] MCP file exists: `C:\AiCOE\AIDA\backend\src\tools\custom_mcp\Databricks_mcp.py`
- [ ] ETL file exists: `C:\AiCOE\AIDA\backend\src\tools\custom_mcp\Databricks_ETL_Generator_mcp.py`

### Step 5B-4: Save and Close
- [ ] Save the file
- [ ] Close the editor

**✅ Done!** Continue to [Step 6: Reload VS Code](#step-6-reload-vs-code-claude-devcline)

---

## ✅ Step 6: Test Integration (GitHub Copilot)

### Quick Test

```powershell
cd C:\AiCOE\AIDA
& .\AIDA\Scripts\Activate.ps1

# Test 1: Import the managerClaude-dev/Cline)

### Try These Commands:

**Test 1: List Clusters**
- [ ] Ask: "List all my Databricks clusters"
- [ ] You should see your clusters

**Test 2: List Warehouses**
- [ ] Ask: "Show me my Databricks SQL warehouses"
- [ ] You should see your warehouses

**Test 3: Create Simple Notebook**
- [ ] Ask: "Create a simple Databricks notebook at /Users/me/test with hello world code"
- [ ] Notebook should be created

**Test 4: Generate ETL (Advanced)**
- [ ] Ask: "Generate a Databricks ETL notebook with one simple mapping from CSV to Delta"
- [ ] ETL code should be generated

**All working?** 🎉 **Setup Complete!**

---

## 🎯 Verification Summary

- [ ] ✅ Databricks credentials configured in `.env`
- [ ] ✅ Dependencies installed
- [ ] ✅ Test script passed all checks
- [ ] ✅ MCP settings configured
- [ ] ✅ VS Code reloaded
- [ ] ✅ AI can list clusters
- [ ] ✅ AI can query warehouses
- [ ] ✅ Can create notebooks
- [ ] ✅ Can generate ETL notebooks

**Total Time:** 
- Method A (GitHub Copilot): ~10 minutes
- Method B (Claude-dev/Cline):** Import `get_databricks_manager()` in your Python code!

### For Claude-dev/Cline Users (Method B):

Run through this final checklist:
- [ ] Wait for VS Code to reload

---

## ✅ Step 7: Test with AI Assistant (1 minute)

### Try These Commands:

**Test 1: List Clusters**
- [ ] Ask: "List all my Databricks clusters"
- [ ] You should see your clusters

**Test 2: List Warehouses**
- [ ] Ask: "Show me my Databricks SQL warehouses"
- [ ] You should see your warehouses

**Test 3: Create Simple Notebook**
- [ ] Ask: "Create a simple Databricks notebook at /Users/me/test with hello world code"
- [ ] Notebook should be created

**Test 4: Generate ETL (Advanced)**
- [ ] Ask: "Generate a Databricks ETL notebook wit (Claude-dev/Cline only)

**Solution:**
- [ ] Verify MCP config file syntax (use JSON validator)
- [ ] Check paths use double backslashes: `C:\\Path\\To\\File`
- [ ] Reload VS Code window again
- [ ] Restart VS Code completely if needed

### Problem: Import error with databricks_integration (GitHub Copilot)

**Solution:**
```powershell
# Verify the file exists
Test-Path "backend\src\tools\databricks_integration.py"

# Check Python can find the module
python -c "import sys; print('\n'.join(sys.path))"

# Try absolute import
python -c "import importlib.util; spec = importlib.util.spec_from_file_location('databricks_integration', 'backend/src/tools/databricks_integration.py'); module = importlib.util.module_from_spec(spec); print('✅ Module loadable')"
```
## 🎯 Quick Verification Summary

Run through this final checklist:

- [ ] ✅ Databricks credentials configured
- [ ] ✅ `.env` file updated
- [ ] ✅ Dependencies installed
- [ ] ✅ Test script passed all checks
- [ ] ✅ MCP settings configured
- [ ] ✅ VS Code reloaded
- [ ] ✅ AI can list clusters
- [ ] ✅ AI can query warehouses
- [ ] ✅ Can create notebooks
- [ ] ✅ Can generate ETL notebooks

**Total Time:** ~12 minutes

---

## 🆘 Troubleshooting

### Problem: Test script fails with "Module not found"

**Solution:**
```powershell
# Make sure virtual env is activated
& C:\AiCOE\AIDA\AIDA\Scripts\Activate.ps1

# Reinstall packages
pip install --upgrade python-dotenv mcp requests
```

### Problem: "401 Authentication Error"

**Solution:**
- [ ] Check token hasn't expired
- [ ] Verify token is copied correctly (no spaces)
- [ ] Regenerate token if needed
- [ ] Update both .env and cline_mcp_settings.json

### Problem: AI doesn't recognize Databricks tools

**Solution:**
- [ ] Verify MCP config file syntax (use JSON validator)
- [ ] Check paths use double backslashes: `C:\\Path\\To\\File`
- [ ] Reload VS Code window again
- [ ] Restart VS Code completely if needed

### Problem: "Path not found" errors

**Solution:**
- [ ] Verify Python path: `C:\AiCOE\AIDA\AIDA\Scripts\python.exe`
- [ ] Check file exists: `backend\src\tools\custom_mcp\Databricks_mcp.py`
- [ ] Use absolute paths in MCP config
- [ ] Check for typos in paths

### Problem: Can list clusters but can't generate notebooks

**Solution:**
- [ ] Check both tools are configured in MCP settings
- [ ] Verify `databricks-etl` server is in config
- [ ] Reload window after config changes
- [ ] Check logs for errors

---

## 📚 What's Next?

Now that setup is complete, explore these resources:

### Learn the Basics
1. [ ] Read [Quick Reference](./DATABRICKS_QUICK_REF.md)
2. [ ] Try [Sample Mappings](./SAMPLE_MAPPINGS.md)
3. [ ] Generate your first ETL notebook

### Deep Dive
1. [ ] Study [Complete Workspace Guide](./DATABRICKS_MCP_GUIDE.md)
2. [ ] Master [ETL Generator Guide](./DATABRICKS_ETL_GENERATOR_GUIDE.md)
3. [ ] Review [Implementation Summary](./README_IMPLEMENTATION_SUMMARY.md)

### Start Building
1. [ ] Create test mappings for your data
2. [ ] Generate development notebooks
3. [ ] Test in your workspace
4. [ ] Deploy to production

---

## 🎉 Success!

You're now ready to:
- ✨ Manage Databricks resources with AI
- ⚡ Generate ETL notebooks from mappings
- 🚀 Automate data engineering workflows
- 💪 Build production data pipelines

**Happy Data Engineering!** 🎯

---

## 📞 Need Help?

- **Documentation**: See `*.md` files in this directory
- **Samples**: Check `SAMPLE_MAPPINGS.md`
- **Test**: Run `test_databricks_mcp.py`
- **Databricks Docs**: https://docs.databricks.com/

---

## 🔄 Regular Maintenance

### Weekly
- [ ] Check token expiration
- [ ] Review generated notebooks
- [ ] Update mappings as needed

### Monthly  
- [ ] Rotate access tokens
- [ ] Review cluster usage
- [ ] Optimize notebook performance

### Quarterly
- [ ] Audit security settings
- [ ] Update documentation
- [ ] Train new team members

---

**Setup Version:** 1.0
**Last Updated:** December 24, 2025
**Estimated Setup Time:** 12 minutes
