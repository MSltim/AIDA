import os
import requests
import urllib3
from typing import Dict, List, Optional

from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv(find_dotenv(), verbose=True, override=True)

# SSL Configuration - disable warnings if SSL verification is skipped
SKIP_SSL_VERIFY = os.getenv('DATABRICKS_SKIP_SSL_VERIFY', 'false').lower() == 'true'
if SKIP_SSL_VERIFY:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


mcp = FastMCP("Databricks MCP Server", "0.1.0")

# Databricks Workspace Manager Tool
@mcp.tool()
def DatabricksWorkspaceManagerTool(
    action: str,
    cluster_name: str = None,
    cluster_id: str = None,
    notebook_path: str = None,
    notebook_content: str = None,
    notebook_language: str = "PYTHON",
    job_name: str = None,
    job_id: str = None,
    sql_query: str = None,
    warehouse_id: str = None,
    file_path: str = None,
    file_content: str = None
) -> dict:
    """
    Databricks Workspace Manager Tool - Manage Databricks clusters, notebooks, jobs, and queries.
    
    This tool provides a unified interface for Databricks workspace operations including:
    - List and manage compute clusters
    - Create and manage notebooks
    - Execute SQL queries on SQL warehouses
    - List and manage jobs
    - Manage DBFS (Databricks File System) files
    - Provide usage guidance and error handling
    
    The tool automatically handles Databricks API authentication, validation, 
    and provides structured responses for all operations.
    
    Args:
        action (str): The action to perform. Options:
            - "list_clusters": Show all available compute clusters
            - "get_cluster": Get details for a specific cluster by name or ID
            - "start_cluster": Start a stopped cluster
            - "stop_cluster": Stop a running cluster
            - "create_notebook": Create a new notebook in the workspace
            - "list_notebooks": List notebooks in a specific path
            - "run_sql_query": Execute a SQL query on a SQL warehouse
            - "list_jobs": Show all jobs in the workspace
            - "get_job": Get details for a specific job
            - "run_job": Trigger a job run
            - "list_warehouses": Show all SQL warehouses
            - "upload_file": Upload a file to DBFS
            - "list_dbfs": List files in DBFS path
            - "help" or "guide": Show usage instructions
            
        cluster_name (str, optional): The name of the cluster
        cluster_id (str, optional): The ID of the cluster
        notebook_path (str, optional): Path where notebook should be created (e.g., "/Users/user@example.com/my_notebook")
        notebook_content (str, optional): Content of the notebook
        notebook_language (str, optional): Language of notebook ("PYTHON", "SQL", "SCALA", "R")
        job_name (str, optional): Name of the job
        job_id (str, optional): ID of the job
        sql_query (str, optional): SQL query to execute
        warehouse_id (str, optional): SQL warehouse ID
        file_path (str, optional): DBFS file path
        file_content (str, optional): Content to upload to file
    
    Returns:
        dict: Standardized response with success status, data, and messages
    
    Examples:
        # List all clusters
        DatabricksWorkspaceManagerTool(action="list_clusters")
        
        # Get specific cluster details
        DatabricksWorkspaceManagerTool(
            action="get_cluster",
            cluster_name="my-cluster"
        )
        
        # Start a cluster
        DatabricksWorkspaceManagerTool(
            action="start_cluster",
            cluster_id="0123-456789-abcd1234"
        )
        
        # Create a new notebook
        DatabricksWorkspaceManagerTool(
            action="create_notebook",
            notebook_path="/Users/user@example.com/analysis",
            notebook_content="print('Hello Databricks')",
            notebook_language="PYTHON"
        )
        
        # Run SQL query
        DatabricksWorkspaceManagerTool(
            action="run_sql_query",
            sql_query="SELECT * FROM my_table LIMIT 10",
            warehouse_id="abc123def456"
        )
        
        # List all jobs
        DatabricksWorkspaceManagerTool(action="list_jobs")
        
        # Get help
        DatabricksWorkspaceManagerTool(action="help")
    """
    
    # Validate required environment variables
    try:
        databricks_host = os.getenv('DATABRICKS_HOST')
        databricks_token = os.getenv('DATABRICKS_TOKEN')
        
        if not databricks_host:
            return {
                "success": False,
                "error": "Missing environment variable: DATABRICKS_HOST",
                "message": "Please ensure DATABRICKS_HOST is set in your environment (e.g., https://your-workspace.cloud.databricks.com)."
            }
        
        if not databricks_token:
            return {
                "success": False,
                "error": "Missing environment variable: DATABRICKS_TOKEN",
                "message": "Please ensure DATABRICKS_TOKEN is set in your environment."
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Configuration error: {str(e)}",
            "message": "Please ensure DATABRICKS_HOST and DATABRICKS_TOKEN are set in your environment."
        }
    
    # Normalize action parameter
    action = action.lower().strip()
    
    # Helper function to make Databricks API requests
    def _make_databricks_request(endpoint, method="GET", data=None, api_version="2.0"):
        """Make authenticated Databricks API request"""
        url = f"{databricks_host.rstrip('/')}/api/{api_version}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {databricks_token}",
            "Content-Type": "application/json"
        }
        
        # Determine SSL verification setting
        verify_ssl = not SKIP_SSL_VERIFY
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, verify=verify_ssl)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, verify=verify_ssl)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, verify=verify_ssl)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, json=data, verify=verify_ssl)
            else:
                return None, {"error": f"Unsupported HTTP method: {method}"}
            
            return response, None
        except Exception as e:
            return None, {"error": f"Request failed: {str(e)}"}
    
    # Action: List all clusters
    if action in ["list_clusters", "show_clusters", "clusters", "list"]:
        try:
            response, error = _make_databricks_request("clusters/list")
            if error:
                return {
                    "success": False,
                    "action": "list_clusters",
                    "error": error["error"],
                    "message": "Failed to fetch Databricks clusters."
                }
            
            if response.status_code == 200:
                data = response.json()
                clusters = data.get("clusters", [])
                
                cluster_info = []
                for cluster in clusters:
                    cluster_info.append({
                        "cluster_id": cluster.get("cluster_id"),
                        "cluster_name": cluster.get("cluster_name"),
                        "state": cluster.get("state"),
                        "spark_version": cluster.get("spark_version"),
                        "node_type_id": cluster.get("node_type_id"),
                        "num_workers": cluster.get("num_workers", 0)
                    })
                
                return {
                    "success": True,
                    "action": "list_clusters",
                    "data": {
                        "clusters": cluster_info,
                        "count": len(cluster_info)
                    },
                    "message": f"Found {len(cluster_info)} Databricks clusters."
                }
            else:
                return {
                    "success": False,
                    "action": "list_clusters",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to fetch clusters. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "list_clusters",
                "error": str(e),
                "message": "An unexpected error occurred while fetching clusters."
            }
    
    # Action: Get specific cluster details
    elif action in ["get_cluster", "cluster_details", "cluster_info"]:
        if not cluster_id and not cluster_name:
            return {
                "success": False,
                "action": "get_cluster",
                "error": "Missing required parameters",
                "message": "Please provide either cluster_id or cluster_name.",
                "usage": "DatabricksWorkspaceManagerTool(action='get_cluster', cluster_id='0123-456789-abcd1234')"
            }
        
        try:
            # If cluster_name provided, get all clusters and find the ID
            if cluster_name and not cluster_id:
                response, error = _make_databricks_request("clusters/list")
                if error or response.status_code != 200:
                    return {
                        "success": False,
                        "action": "get_cluster",
                        "error": "Failed to list clusters",
                        "message": "Could not retrieve cluster list to find cluster by name."
                    }
                
                clusters = response.json().get("clusters", [])
                for cluster in clusters:
                    if cluster.get("cluster_name") == cluster_name:
                        cluster_id = cluster.get("cluster_id")
                        break
                
                if not cluster_id:
                    available_clusters = [c.get("cluster_name") for c in clusters[:5]]
                    return {
                        "success": False,
                        "action": "get_cluster",
                        "error": "Cluster not found",
                        "message": f"Cluster '{cluster_name}' not found.",
                        "hint": f"Available clusters (first 5): {', '.join(available_clusters)}",
                        "suggestion": "Use DatabricksWorkspaceManagerTool(action='list_clusters') to see all available clusters."
                    }
            
            # Get cluster details
            response, error = _make_databricks_request("clusters/get", data={"cluster_id": cluster_id})
            if error:
                return {
                    "success": False,
                    "action": "get_cluster",
                    "error": error["error"],
                    "message": "Failed to fetch cluster details."
                }
            
            if response.status_code == 200:
                cluster_data = response.json()
                return {
                    "success": True,
                    "action": "get_cluster",
                    "data": cluster_data,
                    "message": f"Successfully retrieved details for cluster '{cluster_data.get('cluster_name')}'"
                }
            else:
                return {
                    "success": False,
                    "action": "get_cluster",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to fetch cluster details. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "get_cluster",
                "error": str(e),
                "message": "An unexpected error occurred while fetching cluster details."
            }
    
    # Action: Start cluster
    elif action in ["start_cluster", "start"]:
        if not cluster_id:
            return {
                "success": False,
                "action": "start_cluster",
                "error": "Missing required parameter",
                "message": "Please provide cluster_id to start a cluster.",
                "usage": "DatabricksWorkspaceManagerTool(action='start_cluster', cluster_id='0123-456789-abcd1234')"
            }
        
        try:
            response, error = _make_databricks_request("clusters/start", method="POST", data={"cluster_id": cluster_id})
            if error:
                return {
                    "success": False,
                    "action": "start_cluster",
                    "error": error["error"],
                    "message": "Failed to start cluster."
                }
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "action": "start_cluster",
                    "data": {"cluster_id": cluster_id},
                    "message": f"Cluster '{cluster_id}' start initiated successfully."
                }
            else:
                return {
                    "success": False,
                    "action": "start_cluster",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to start cluster. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "start_cluster",
                "error": str(e),
                "message": "An unexpected error occurred while starting cluster."
            }
    
    # Action: Stop cluster
    elif action in ["stop_cluster", "stop"]:
        if not cluster_id:
            return {
                "success": False,
                "action": "stop_cluster",
                "error": "Missing required parameter",
                "message": "Please provide cluster_id to stop a cluster.",
                "usage": "DatabricksWorkspaceManagerTool(action='stop_cluster', cluster_id='0123-456789-abcd1234')"
            }
        
        try:
            response, error = _make_databricks_request("clusters/delete", method="POST", data={"cluster_id": cluster_id})
            if error:
                return {
                    "success": False,
                    "action": "stop_cluster",
                    "error": error["error"],
                    "message": "Failed to stop cluster."
                }
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "action": "stop_cluster",
                    "data": {"cluster_id": cluster_id},
                    "message": f"Cluster '{cluster_id}' stop initiated successfully."
                }
            else:
                return {
                    "success": False,
                    "action": "stop_cluster",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to stop cluster. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "stop_cluster",
                "error": str(e),
                "message": "An unexpected error occurred while stopping cluster."
            }
    
    # Action: Create notebook
    elif action in ["create_notebook", "new_notebook", "add_notebook"]:
        if not notebook_path:
            return {
                "success": False,
                "action": "create_notebook",
                "error": "Missing required parameter",
                "message": "Please provide notebook_path (e.g., '/Users/user@example.com/my_notebook').",
                "usage": "DatabricksWorkspaceManagerTool(action='create_notebook', notebook_path='/path/to/notebook', notebook_content='code')"
            }
        
        try:
            import base64
            
            # Encode content to base64
            content = notebook_content or "# New Notebook\nprint('Hello Databricks')"
            content_b64 = base64.b64encode(content.encode()).decode()
            
            data = {
                "path": notebook_path,
                "format": "SOURCE",
                "language": notebook_language.upper(),
                "content": content_b64,
                "overwrite": False
            }
            
            response, error = _make_databricks_request("workspace/import", method="POST", data=data)
            if error:
                return {
                    "success": False,
                    "action": "create_notebook",
                    "error": error["error"],
                    "message": "Failed to create notebook."
                }
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "action": "create_notebook",
                    "data": {
                        "notebook_path": notebook_path,
                        "language": notebook_language
                    },
                    "message": f"Notebook created successfully at '{notebook_path}'"
                }
            else:
                return {
                    "success": False,
                    "action": "create_notebook",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to create notebook. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "create_notebook",
                "error": str(e),
                "message": "An unexpected error occurred while creating notebook."
            }
    
    # Action: List notebooks
    elif action in ["list_notebooks", "show_notebooks", "notebooks"]:
        if not notebook_path:
            notebook_path = "/"
        
        try:
            response, error = _make_databricks_request("workspace/list", data={"path": notebook_path})
            if error:
                return {
                    "success": False,
                    "action": "list_notebooks",
                    "error": error["error"],
                    "message": "Failed to list notebooks."
                }
            
            if response.status_code == 200:
                data = response.json()
                objects = data.get("objects", [])
                
                return {
                    "success": True,
                    "action": "list_notebooks",
                    "data": {
                        "path": notebook_path,
                        "objects": objects,
                        "count": len(objects)
                    },
                    "message": f"Found {len(objects)} items in '{notebook_path}'"
                }
            else:
                return {
                    "success": False,
                    "action": "list_notebooks",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to list notebooks. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "list_notebooks",
                "error": str(e),
                "message": "An unexpected error occurred while listing notebooks."
            }
    
    # Action: Run SQL query
    elif action in ["run_sql_query", "execute_sql", "sql_query", "query"]:
        if not sql_query:
            return {
                "success": False,
                "action": "run_sql_query",
                "error": "Missing required parameter",
                "message": "Please provide sql_query to execute.",
                "usage": "DatabricksWorkspaceManagerTool(action='run_sql_query', sql_query='SELECT * FROM table', warehouse_id='abc123')"
            }
        
        if not warehouse_id:
            return {
                "success": False,
                "action": "run_sql_query",
                "error": "Missing required parameter",
                "message": "Please provide warehouse_id. Use action='list_warehouses' to see available warehouses.",
                "usage": "DatabricksWorkspaceManagerTool(action='run_sql_query', sql_query='SELECT * FROM table', warehouse_id='abc123')"
            }
        
        try:
            data = {
                "warehouse_id": warehouse_id,
                "statement": sql_query,
                "wait_timeout": "30s"
            }
            
            response, error = _make_databricks_request("sql/statements", method="POST", data=data, api_version="2.0")
            if error:
                return {
                    "success": False,
                    "action": "run_sql_query",
                    "error": error["error"],
                    "message": "Failed to execute SQL query."
                }
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "action": "run_sql_query",
                    "data": result,
                    "message": f"SQL query executed successfully. State: {result.get('status', {}).get('state')}"
                }
            else:
                return {
                    "success": False,
                    "action": "run_sql_query",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to execute SQL query. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "run_sql_query",
                "error": str(e),
                "message": "An unexpected error occurred while executing SQL query."
            }
    
    # Action: List jobs
    elif action in ["list_jobs", "show_jobs", "jobs"]:
        try:
            response, error = _make_databricks_request("jobs/list")
            if error:
                return {
                    "success": False,
                    "action": "list_jobs",
                    "error": error["error"],
                    "message": "Failed to fetch jobs."
                }
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("jobs", [])
                
                job_info = []
                for job in jobs:
                    job_info.append({
                        "job_id": job.get("job_id"),
                        "job_name": job.get("settings", {}).get("name"),
                        "created_time": job.get("created_time")
                    })
                
                return {
                    "success": True,
                    "action": "list_jobs",
                    "data": {
                        "jobs": job_info,
                        "count": len(job_info)
                    },
                    "message": f"Found {len(job_info)} Databricks jobs."
                }
            else:
                return {
                    "success": False,
                    "action": "list_jobs",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to fetch jobs. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "list_jobs",
                "error": str(e),
                "message": "An unexpected error occurred while fetching jobs."
            }
    
    # Action: Get job details
    elif action in ["get_job", "job_details", "job_info"]:
        if not job_id:
            return {
                "success": False,
                "action": "get_job",
                "error": "Missing required parameter",
                "message": "Please provide job_id.",
                "usage": "DatabricksWorkspaceManagerTool(action='get_job', job_id='12345')"
            }
        
        try:
            response, error = _make_databricks_request("jobs/get", data={"job_id": int(job_id)})
            if error:
                return {
                    "success": False,
                    "action": "get_job",
                    "error": error["error"],
                    "message": "Failed to fetch job details."
                }
            
            if response.status_code == 200:
                job_data = response.json()
                return {
                    "success": True,
                    "action": "get_job",
                    "data": job_data,
                    "message": f"Successfully retrieved details for job ID {job_id}"
                }
            else:
                return {
                    "success": False,
                    "action": "get_job",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to fetch job details. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "get_job",
                "error": str(e),
                "message": "An unexpected error occurred while fetching job details."
            }
    
    # Action: Run job
    elif action in ["run_job", "trigger_job", "execute_job"]:
        if not job_id:
            return {
                "success": False,
                "action": "run_job",
                "error": "Missing required parameter",
                "message": "Please provide job_id.",
                "usage": "DatabricksWorkspaceManagerTool(action='run_job', job_id='12345')"
            }
        
        try:
            response, error = _make_databricks_request("jobs/run-now", method="POST", data={"job_id": int(job_id)})
            if error:
                return {
                    "success": False,
                    "action": "run_job",
                    "error": error["error"],
                    "message": "Failed to run job."
                }
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "action": "run_job",
                    "data": result,
                    "message": f"Job {job_id} triggered successfully. Run ID: {result.get('run_id')}"
                }
            else:
                return {
                    "success": False,
                    "action": "run_job",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to run job. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "run_job",
                "error": str(e),
                "message": "An unexpected error occurred while running job."
            }
    
    # Action: List SQL warehouses
    elif action in ["list_warehouses", "show_warehouses", "warehouses"]:
        try:
            response, error = _make_databricks_request("sql/warehouses", api_version="2.0")
            if error:
                return {
                    "success": False,
                    "action": "list_warehouses",
                    "error": error["error"],
                    "message": "Failed to fetch SQL warehouses."
                }
            
            if response.status_code == 200:
                data = response.json()
                warehouses = data.get("warehouses", [])
                
                warehouse_info = []
                for warehouse in warehouses:
                    warehouse_info.append({
                        "id": warehouse.get("id"),
                        "name": warehouse.get("name"),
                        "state": warehouse.get("state"),
                        "cluster_size": warehouse.get("cluster_size")
                    })
                
                return {
                    "success": True,
                    "action": "list_warehouses",
                    "data": {
                        "warehouses": warehouse_info,
                        "count": len(warehouse_info)
                    },
                    "message": f"Found {len(warehouse_info)} SQL warehouses."
                }
            else:
                return {
                    "success": False,
                    "action": "list_warehouses",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to fetch warehouses. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "list_warehouses",
                "error": str(e),
                "message": "An unexpected error occurred while fetching warehouses."
            }
    
    # Action: List DBFS files
    elif action in ["list_dbfs", "show_dbfs", "dbfs"]:
        if not file_path:
            file_path = "/"
        
        try:
            response, error = _make_databricks_request("dbfs/list", data={"path": file_path})
            if error:
                return {
                    "success": False,
                    "action": "list_dbfs",
                    "error": error["error"],
                    "message": "Failed to list DBFS files."
                }
            
            if response.status_code == 200:
                data = response.json()
                files = data.get("files", [])
                
                return {
                    "success": True,
                    "action": "list_dbfs",
                    "data": {
                        "path": file_path,
                        "files": files,
                        "count": len(files)
                    },
                    "message": f"Found {len(files)} items in DBFS path '{file_path}'"
                }
            else:
                return {
                    "success": False,
                    "action": "list_dbfs",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to list DBFS files. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "list_dbfs",
                "error": str(e),
                "message": "An unexpected error occurred while listing DBFS files."
            }
    
    # Action: Upload file to DBFS
    elif action in ["upload_file", "upload_to_dbfs", "put_file"]:
        if not file_path or not file_content:
            return {
                "success": False,
                "action": "upload_file",
                "error": "Missing required parameters",
                "message": "Please provide both file_path and file_content.",
                "usage": "DatabricksWorkspaceManagerTool(action='upload_file', file_path='/path/to/file.txt', file_content='content')"
            }
        
        try:
            import base64
            
            # Encode content to base64
            content_b64 = base64.b64encode(file_content.encode()).decode()
            
            data = {
                "path": file_path,
                "contents": content_b64,
                "overwrite": True
            }
            
            response, error = _make_databricks_request("dbfs/put", method="POST", data=data)
            if error:
                return {
                    "success": False,
                    "action": "upload_file",
                    "error": error["error"],
                    "message": "Failed to upload file to DBFS."
                }
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "action": "upload_file",
                    "data": {
                        "file_path": file_path
                    },
                    "message": f"File uploaded successfully to '{file_path}'"
                }
            else:
                return {
                    "success": False,
                    "action": "upload_file",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to upload file. Status: {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "upload_file",
                "error": str(e),
                "message": "An unexpected error occurred while uploading file."
            }
    
    # Action: Help/Guide
    elif action in ["help", "guide", "usage", "instructions"]:
        help_message = """
[DATABRICKS] Databricks Workspace Manager Tool - Usage Guide

Available Actions:

CLUSTER MANAGEMENT:
1. 'list_clusters' - Show all available compute clusters
2. 'get_cluster' - Get details for a specific cluster
3. 'start_cluster' - Start a stopped cluster
4. 'stop_cluster' - Stop a running cluster

NOTEBOOK MANAGEMENT:
5. 'create_notebook' - Create a new notebook
6. 'list_notebooks' - List notebooks in a path

SQL OPERATIONS:
7. 'run_sql_query' - Execute SQL query on warehouse
8. 'list_warehouses' - Show all SQL warehouses

JOB MANAGEMENT:
9. 'list_jobs' - Show all jobs
10. 'get_job' - Get job details
11. 'run_job' - Trigger a job run

FILE SYSTEM:
12. 'list_dbfs' - List files in DBFS
13. 'upload_file' - Upload file to DBFS

14. 'help' - Show this guide

[EXAMPLES] Examples:

# List all clusters
DatabricksWorkspaceManagerTool(action="list_clusters")

# Get cluster details
DatabricksWorkspaceManagerTool(
    action="get_cluster",
    cluster_name="my-cluster"
)

# Start a cluster
DatabricksWorkspaceManagerTool(
    action="start_cluster",
    cluster_id="0123-456789-abcd1234"
)

# Create a Python notebook
DatabricksWorkspaceManagerTool(
    action="create_notebook",
    notebook_path="/Users/user@example.com/analysis",
    notebook_content="df = spark.read.csv('/data/file.csv')",
    notebook_language="PYTHON"
)

# Run SQL query
DatabricksWorkspaceManagerTool(
    action="run_sql_query",
    sql_query="SELECT COUNT(*) FROM customers",
    warehouse_id="abc123def456"
)

# List all jobs
DatabricksWorkspaceManagerTool(action="list_jobs")

# Trigger a job
DatabricksWorkspaceManagerTool(
    action="run_job",
    job_id="12345"
)

# Upload file to DBFS
DatabricksWorkspaceManagerTool(
    action="upload_file",
    file_path="/FileStore/data/config.json",
    file_content='{"key": "value"}'
)

[TIPS] Tips:
- Get your workspace URL from Databricks (e.g., https://your-workspace.cloud.databricks.com)
- Generate a personal access token in User Settings > Access Tokens
- Cluster IDs are in format: 0123-456789-abcd1234
- Notebook paths should start with /Users/ or /Shared/
- SQL queries require a warehouse_id - use list_warehouses first
- DBFS paths typically start with / or /FileStore/
        """
        
        return {
            "success": True,
            "action": "help",
            "data": {
                "available_actions": [
                    "list_clusters", "get_cluster", "start_cluster", "stop_cluster",
                    "create_notebook", "list_notebooks",
                    "run_sql_query", "list_warehouses",
                    "list_jobs", "get_job", "run_job",
                    "list_dbfs", "upload_file",
                    "help"
                ],
                "examples_provided": True
            },
            "message": help_message
        }
    
    # Invalid action
    else:
        return {
            "success": False,
            "error": f"Invalid action: '{action}'",
            "message": "Use action='help' for a list of valid actions and usage instructions.",
            "usage": "DatabricksWorkspaceManagerTool(action='help') for detailed usage instructions"
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
