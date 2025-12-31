# Databricks MCP Server - Setup and Usage Guide

## Overview
The Databricks MCP (Model Context Protocol) server provides a unified interface to interact with your Databricks workspace, enabling cluster management, notebook operations, SQL queries, job execution, and DBFS file operations through a simple API.

## Features
- **Cluster Management**: List, get details, start, and stop compute clusters
- **Notebook Operations**: Create and list notebooks in your workspace
- **SQL Execution**: Run SQL queries on SQL warehouses
- **Job Management**: List, get details, and trigger job runs
- **File System**: Upload files and list DBFS contents

---

## Setup Instructions

### Step 1: Install Required Dependencies

Make sure you have the required Python packages installed:

```bash
pip install python-dotenv mcp requests
```

Or add to your `requirements.txt`:
```
python-dotenv
mcp
requests
```

### Step 2: Get Databricks Credentials

#### 2.1 Get Your Workspace URL
Your Databricks workspace URL looks like:
- **Azure**: `https://adb-1234567890123456.7.azuredatabricks.net`
- **AWS**: `https://your-workspace.cloud.databricks.com`
- **GCP**: `https://your-account-id.gcp.databricks.com`

You can find this in your browser's address bar when logged into Databricks.

#### 2.2 Generate a Personal Access Token

1. Log in to your Databricks workspace
2. Click on your username in the top-right corner
3. Select **User Settings**
4. Go to **Access Tokens** tab (or **Developer** > **Access tokens**)
5. Click **Generate New Token**
6. Give it a description (e.g., "MCP Server Token")
7. Set an expiration period (or leave blank for no expiration)
8. Click **Generate**
9. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

### Step 3: Configure Environment Variables

Create or update your `.env` file with the following variables:

```env
# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=<databricks_api_token>
```

**Example `.env` file:**
```env
# Databricks Credentials
DATABRICKS_HOST=https://adb-1234567890123456.7.azuredatabricks.net
DATABRICKS_TOKEN=<databricks_api_token>

# Other configurations...
```

### Step 4: Configure MCP Settings

Update your MCP configuration file to include the Databricks server.

**For Windows - Edit `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`:**

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
        "DATABRICKS_TOKEN": "your-databricks-token"
      }
    }
  }
}
```

**For Mac/Linux:**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "/path/to/your/venv/bin/python",
      "args": [
        "/path/to/Databricks_mcp.py"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-databricks-token"
      }
    }
  }
}
```

### Step 5: Test the Connection

Run the MCP server directly to test:

```bash
# Activate your virtual environment
C:\AiCOE\AIDA\AIDA\Scripts\activate

# Run the server
python C:\AiCOE\AIDA\backend\src\tools\custom_mcp\Databricks_mcp.py
```

---

## Usage Examples

### 1. Cluster Management

#### List All Clusters
```python
from Databricks_mcp import DatabricksWorkspaceManagerTool

# List all available clusters
result = DatabricksWorkspaceManagerTool(action="list_clusters")
print(result)
```

**Output:**
```json
{
  "success": true,
  "action": "list_clusters",
  "data": {
    "clusters": [
      {
        "cluster_id": "0123-456789-abcd1234",
        "cluster_name": "my-cluster",
        "state": "RUNNING",
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "Standard_DS3_v2",
        "num_workers": 2
      }
    ],
    "count": 1
  },
  "message": "Found 1 Databricks clusters."
}
```

#### Get Cluster Details
```python
# Get details by cluster name
result = DatabricksWorkspaceManagerTool(
    action="get_cluster",
    cluster_name="my-cluster"
)

# Or by cluster ID
result = DatabricksWorkspaceManagerTool(
    action="get_cluster",
    cluster_id="0123-456789-abcd1234"
)
```

#### Start a Cluster
```python
result = DatabricksWorkspaceManagerTool(
    action="start_cluster",
    cluster_id="0123-456789-abcd1234"
)
```

#### Stop a Cluster
```python
result = DatabricksWorkspaceManagerTool(
    action="stop_cluster",
    cluster_id="0123-456789-abcd1234"
)
```

### 2. Notebook Operations

#### Create a New Notebook
```python
# Create a Python notebook
result = DatabricksWorkspaceManagerTool(
    action="create_notebook",
    notebook_path="/Users/user@example.com/data_analysis",
    notebook_content="""
# Data Analysis Notebook
import pandas as pd
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
df = spark.read.csv("/data/input.csv", header=True)
df.show(10)
    """,
    notebook_language="PYTHON"
)

# Create a SQL notebook
result = DatabricksWorkspaceManagerTool(
    action="create_notebook",
    notebook_path="/Users/user@example.com/queries",
    notebook_content="SELECT * FROM customers WHERE region = 'US'",
    notebook_language="SQL"
)
```

**Supported Languages:**
- `PYTHON`
- `SQL`
- `SCALA`
- `R`

#### List Notebooks
```python
# List notebooks in a specific path
result = DatabricksWorkspaceManagerTool(
    action="list_notebooks",
    notebook_path="/Users/user@example.com"
)

# List all workspace items
result = DatabricksWorkspaceManagerTool(
    action="list_notebooks",
    notebook_path="/"
)
```

### 3. SQL Operations

#### List SQL Warehouses
```python
result = DatabricksWorkspaceManagerTool(action="list_warehouses")
```

**Output:**
```json
{
  "success": true,
  "data": {
    "warehouses": [
      {
        "id": "abc123def456",
        "name": "Starter Warehouse",
        "state": "RUNNING",
        "cluster_size": "Small"
      }
    ],
    "count": 1
  }
}
```

#### Execute SQL Query
```python
result = DatabricksWorkspaceManagerTool(
    action="run_sql_query",
    sql_query="SELECT COUNT(*) as total_customers FROM customers",
    warehouse_id="abc123def456"
)

# More complex query
result = DatabricksWorkspaceManagerTool(
    action="run_sql_query",
    sql_query="""
        SELECT 
            region,
            COUNT(*) as customer_count,
            AVG(order_value) as avg_order_value
        FROM customers
        WHERE signup_date >= '2024-01-01'
        GROUP BY region
        ORDER BY customer_count DESC
    """,
    warehouse_id="abc123def456"
)
```

### 4. Job Management

#### List All Jobs
```python
result = DatabricksWorkspaceManagerTool(action="list_jobs")
```

**Output:**
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "job_id": 12345,
        "job_name": "Daily ETL Pipeline",
        "created_time": 1703001234567
      }
    ],
    "count": 1
  }
}
```

#### Get Job Details
```python
result = DatabricksWorkspaceManagerTool(
    action="get_job",
    job_id="12345"
)
```

#### Trigger a Job Run
```python
result = DatabricksWorkspaceManagerTool(
    action="run_job",
    job_id="12345"
)
```

**Output:**
```json
{
  "success": true,
  "action": "run_job",
  "data": {
    "run_id": 67890
  },
  "message": "Job 12345 triggered successfully. Run ID: 67890"
}
```

### 5. File System (DBFS) Operations

#### List Files in DBFS
```python
# List root directory
result = DatabricksWorkspaceManagerTool(
    action="list_dbfs",
    file_path="/"
)

# List FileStore
result = DatabricksWorkspaceManagerTool(
    action="list_dbfs",
    file_path="/FileStore"
)
```

#### Upload File to DBFS
```python
# Upload a JSON configuration file
result = DatabricksWorkspaceManagerTool(
    action="upload_file",
    file_path="/FileStore/configs/app_config.json",
    file_content='{"environment": "production", "debug": false}'
)

# Upload a CSV file (content as string)
csv_content = """name,age,city
Alice,30,New York
Bob,25,San Francisco
Charlie,35,Boston"""

result = DatabricksWorkspaceManagerTool(
    action="upload_file",
    file_path="/FileStore/data/users.csv",
    file_content=csv_content
)
```

### 6. Get Help
```python
result = DatabricksWorkspaceManagerTool(action="help")
print(result["message"])
```

---

## Using with AI Assistants (Claude, etc.)

Once configured, you can ask your AI assistant natural language questions:

**Example Conversations:**

1. **"List all my Databricks clusters"**
   - The AI will call `DatabricksWorkspaceManagerTool(action="list_clusters")`

2. **"Start the cluster named 'analytics-cluster'"**
   - The AI will first get the cluster to find its ID, then start it

3. **"Create a Python notebook called 'sales_analysis' in my user folder with basic spark code"**
   - The AI will create the notebook with appropriate content

4. **"Run this SQL query: SELECT * FROM sales WHERE date >= '2024-01-01' LIMIT 10"**
   - The AI will first list warehouses, then execute the query

5. **"What jobs do I have and trigger the ETL job"**
   - The AI will list jobs, find the ETL job, and trigger it

---

## Common Use Cases

### Use Case 1: Automated Cluster Management
```python
# Start cluster before running analysis
start_result = DatabricksWorkspaceManagerTool(
    action="start_cluster",
    cluster_id="0123-456789-abcd1234"
)

# Wait for cluster to be ready (you'd implement polling in production)
# ... do your work ...

# Stop cluster to save costs
stop_result = DatabricksWorkspaceManagerTool(
    action="stop_cluster",
    cluster_id="0123-456789-abcd1234"
)
```

### Use Case 2: Daily Report Generation
```python
# 1. Ensure warehouse is available
warehouses = DatabricksWorkspaceManagerTool(action="list_warehouses")
warehouse_id = warehouses["data"]["warehouses"][0]["id"]

# 2. Run the report query
report = DatabricksWorkspaceManagerTool(
    action="run_sql_query",
    sql_query="""
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as transactions,
            SUM(amount) as total_revenue
        FROM transactions
        WHERE DATE(timestamp) = CURRENT_DATE - INTERVAL 1 DAY
        GROUP BY DATE(timestamp)
    """,
    warehouse_id=warehouse_id
)

# 3. Process and save results
# ... your processing logic ...
```

### Use Case 3: Scheduled ETL Pipeline
```python
# List all jobs to find ETL jobs
jobs = DatabricksWorkspaceManagerTool(action="list_jobs")

# Find and run specific ETL job
for job in jobs["data"]["jobs"]:
    if "ETL" in job["job_name"]:
        result = DatabricksWorkspaceManagerTool(
            action="run_job",
            job_id=str(job["job_id"])
        )
        print(f"Triggered {job['job_name']}: Run ID {result['data']['run_id']}")
```

---

## Error Handling

The tool returns structured error responses:

```python
result = DatabricksWorkspaceManagerTool(
    action="get_cluster",
    cluster_name="non-existent-cluster"
)

if not result["success"]:
    print(f"Error: {result['error']}")
    print(f"Message: {result['message']}")
    if "suggestion" in result:
        print(f"Suggestion: {result['suggestion']}")
```

**Example Error Response:**
```json
{
  "success": false,
  "action": "get_cluster",
  "error": "Cluster not found",
  "message": "Cluster 'non-existent-cluster' not found.",
  "hint": "Available clusters (first 5): analytics, dev-cluster, prod-etl",
  "suggestion": "Use DatabricksWorkspaceManagerTool(action='list_clusters') to see all available clusters."
}
```

---

## Troubleshooting

### Issue 1: Authentication Failed
**Error:** `HTTP 401` or `Authentication failed`

**Solution:**
1. Verify your token is correct and not expired
2. Check that `DATABRICKS_HOST` includes the full URL with `https://`
3. Ensure no extra spaces in environment variables
4. Generate a new token if needed

### Issue 2: Cluster Not Found
**Error:** `Cluster 'xxx' not found`

**Solution:**
1. List all clusters first: `action="list_clusters"`
2. Verify the cluster name/ID matches exactly (case-sensitive)
3. Check that the cluster exists in your workspace

### Issue 3: SQL Query Failed
**Error:** `Failed to execute SQL query`

**Solution:**
1. Check that the warehouse is running
2. List warehouses to get valid warehouse IDs
3. Verify your SQL syntax is correct
4. Ensure you have permissions to access the tables

### Issue 4: Permission Denied
**Error:** `HTTP 403` or `Forbidden`

**Solution:**
1. Check your user permissions in Databricks
2. Verify the token has necessary scopes
3. Contact your Databricks admin for access rights

---

## Security Best Practices

1. **Never commit tokens to version control**
   - Add `.env` to `.gitignore`
   - Use environment variables or secret managers

2. **Use token expiration**
   - Set reasonable expiration times for tokens
   - Rotate tokens periodically

3. **Limit token permissions**
   - Create separate tokens for different purposes
   - Use minimal required permissions

4. **Secure storage**
   - Store tokens in secure vaults (Azure Key Vault, AWS Secrets Manager)
   - Don't share tokens via email or chat

5. **Monitor usage**
   - Regularly review token usage in Databricks
   - Revoke unused or compromised tokens

---

## API Reference

### Available Actions

| Action | Required Parameters | Optional Parameters | Description |
|--------|-------------------|-------------------|-------------|
| `list_clusters` | None | None | List all compute clusters |
| `get_cluster` | `cluster_id` OR `cluster_name` | None | Get cluster details |
| `start_cluster` | `cluster_id` | None | Start a stopped cluster |
| `stop_cluster` | `cluster_id` | None | Stop a running cluster |
| `create_notebook` | `notebook_path` | `notebook_content`, `notebook_language` | Create new notebook |
| `list_notebooks` | None | `notebook_path` | List notebooks |
| `run_sql_query` | `sql_query`, `warehouse_id` | None | Execute SQL query |
| `list_warehouses` | None | None | List SQL warehouses |
| `list_jobs` | None | None | List all jobs |
| `get_job` | `job_id` | None | Get job details |
| `run_job` | `job_id` | None | Trigger job run |
| `list_dbfs` | None | `file_path` | List DBFS files |
| `upload_file` | `file_path`, `file_content` | None | Upload file to DBFS |
| `help` | None | None | Show usage guide |

### Response Format

All responses follow this structure:

```json
{
  "success": true/false,
  "action": "action_name",
  "data": {},
  "message": "Human-readable message",
  "error": "Error details (if success=false)"
}
```

---

## Advanced Configuration

### Using Multiple Workspaces

You can configure multiple Databricks workspaces by creating separate MCP server instances:

```json
{
  "mcpServers": {
    "databricks-prod": {
      "command": "python",
      "args": ["Databricks_mcp.py"],
      "env": {
        "DATABRICKS_HOST": "https://prod-workspace.databricks.com",
        "DATABRICKS_TOKEN": "prod-token"
      }
    },
    "databricks-dev": {
      "command": "python",
      "args": ["Databricks_mcp.py"],
      "env": {
        "DATABRICKS_HOST": "https://dev-workspace.databricks.com",
        "DATABRICKS_TOKEN": "dev-token"
      }
    }
  }
}
```

### Custom Timeout Configuration

For long-running queries, you might want to adjust timeouts in the code:

```python
# In run_sql_query action
data = {
    "warehouse_id": warehouse_id,
    "statement": sql_query,
    "wait_timeout": "120s"  # Increase timeout
}
```

---

## Support and Resources

### Official Databricks Documentation
- [Databricks REST API](https://docs.databricks.com/api/workspace/introduction)
- [Authentication](https://docs.databricks.com/dev-tools/auth.html)
- [Clusters API](https://docs.databricks.com/api/workspace/clusters)
- [SQL API](https://docs.databricks.com/sql/api/index.html)

### Common Issues
- Check Databricks status page for outages
- Review API rate limits
- Check your workspace plan features

---

## Changelog

### Version 0.1.0 (Initial Release)
- Cluster management (list, get, start, stop)
- Notebook operations (create, list)
- SQL query execution
- Job management (list, get, run)
- DBFS file operations
- Comprehensive error handling
- Help system

---

## License

This tool is part of the AIDA project. Please refer to the project's main license file.

---

## Contributing

If you'd like to add features or fix bugs:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

**Feature Requests:**
- Workspace export/import
- Delta table operations
- Cluster creation/deletion
- Advanced job scheduling
- Unity Catalog operations

---

## Quick Start Checklist

- [ ] Install dependencies (`pip install python-dotenv mcp requests`)
- [ ] Get Databricks workspace URL
- [ ] Generate personal access token
- [ ] Create/update `.env` file with credentials
- [ ] Configure MCP settings JSON
- [ ] Test connection with `list_clusters`
- [ ] Try creating a simple notebook
- [ ] Run a test SQL query
- [ ] Review help documentation (`action="help"`)

---

**Need Help?** Open an issue in the project repository with:
- Your OS and Python version
- Error messages (remove sensitive data)
- What you were trying to accomplish
- Steps to reproduce the issue
