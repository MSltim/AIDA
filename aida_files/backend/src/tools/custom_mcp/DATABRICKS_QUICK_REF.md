# Databricks MCP Server - Quick Reference

## Setup (One-Time)

1. **Install packages:**
   ```bash
   pip install python-dotenv mcp requests
   ```

2. **Get credentials:**
   - Workspace URL: `https://your-workspace.cloud.databricks.com`
   - Token: Databricks → User Settings → Access Tokens → Generate

3. **Add to `.env`:**
   ```env
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=dapi1234567890abcdef...
   ```

4. **Configure MCP (Windows - cline_mcp_settings.json):**
   ```json
   {
     "mcpServers": {
       "databricks": {
         "command": "C:\\AiCOE\\AIDA\\AIDA\\Scripts\\python.exe",
         "args": ["C:\\AiCOE\\AIDA\\backend\\src\\tools\\custom_mcp\\Databricks_mcp.py"],
         "env": {
           "DATABRICKS_HOST": "your-url",
           "DATABRICKS_TOKEN": "your-token"
         }
       }
     }
   }
   ```

5. **Test:**
   ```bash
   python test_databricks_mcp.py
   ```

## Quick Commands

### Clusters
```python
# List all
action="list_clusters"

# Get details
action="get_cluster", cluster_name="my-cluster"

# Start
action="start_cluster", cluster_id="0123-456789-abcd1234"

# Stop
action="stop_cluster", cluster_id="0123-456789-abcd1234"
```

### Notebooks
```python
# Create
action="create_notebook", 
notebook_path="/Users/you@email.com/name",
notebook_content="print('hello')",
notebook_language="PYTHON"

# List
action="list_notebooks", notebook_path="/Users/you@email.com"
```

### SQL
```python
# List warehouses
action="list_warehouses"

# Run query
action="run_sql_query",
sql_query="SELECT * FROM table LIMIT 10",
warehouse_id="abc123"
```

### Jobs
```python
# List all
action="list_jobs"

# Get details
action="get_job", job_id="12345"

# Run
action="run_job", job_id="12345"
```

### DBFS
```python
# List files
action="list_dbfs", file_path="/FileStore"

# Upload
action="upload_file",
file_path="/FileStore/data/file.txt",
file_content="content here"
```

### Help
```python
action="help"
```

## Natural Language (with AI)

Just ask your AI assistant:
- "List my Databricks clusters"
- "Start the analytics cluster"
- "Create a Python notebook for data analysis"
- "Run SQL: SELECT COUNT(*) FROM customers"
- "What jobs do I have?"
- "Upload this config to DBFS /FileStore/config.json"

## Common Workflows

### Daily Report
```python
# 1. Get warehouse
action="list_warehouses"

# 2. Run query
action="run_sql_query", 
sql_query="SELECT date, SUM(revenue) FROM sales GROUP BY date",
warehouse_id="from-step-1"
```

### Start Analysis
```python
# 1. Start cluster
action="start_cluster", cluster_id="your-cluster-id"

# 2. Create notebook
action="create_notebook",
notebook_path="/Users/you/analysis",
notebook_content="# Your code"

# 3. When done, stop cluster
action="stop_cluster", cluster_id="your-cluster-id"
```

### Trigger ETL
```python
# 1. List jobs
action="list_jobs"

# 2. Find ETL job ID from results

# 3. Run job
action="run_job", job_id="found-id"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 401 Auth Error | Check token is valid, not expired |
| Cluster not found | Use `list_clusters` to see available |
| SQL query fails | Verify warehouse ID with `list_warehouses` |
| Module not found | Run `pip install python-dotenv mcp requests` |

## File Locations

- **MCP Server:** `backend/src/tools/custom_mcp/Databricks_mcp.py`
- **Test Script:** `backend/src/tools/custom_mcp/test_databricks_mcp.py`
- **Full Guide:** `backend/src/tools/custom_mcp/DATABRICKS_MCP_GUIDE.md`
- **Config:** `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

## Resources

- [Full Setup Guide](./DATABRICKS_MCP_GUIDE.md)
- [Databricks API Docs](https://docs.databricks.com/api/)
- [Generate Token](https://docs.databricks.com/dev-tools/auth.html)
