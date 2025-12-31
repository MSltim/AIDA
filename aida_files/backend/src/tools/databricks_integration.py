"""
Databricks Integration for AIDA
Provides direct access to Databricks MCP tools without requiring MCP server configuration.

This module wraps the Databricks MCP and ETL Generator MCP tools, making them
available as a standard Python API that can be imported and used throughout
the AIDA application.

Usage:
    from backend.src.tools.databricks_integration import get_databricks_manager
    
    db = get_databricks_manager()
    clusters = db.list_clusters()
    print(f"Found {len(clusters)} clusters")

Author: AIDA Team
Date: December 24, 2025
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add custom_mcp directory to Python path
CUSTOM_MCP_PATH = Path(__file__).parent / "custom_mcp"
if str(CUSTOM_MCP_PATH) not in sys.path:
    sys.path.insert(0, str(CUSTOM_MCP_PATH))

# Import Databricks modules
try:
    from Databricks_mcp import DatabricksWorkspaceManagerTool
    from Databricks_ETL_Generator_mcp import DatabricksETLNotebookGenerator
    DATABRICKS_AVAILABLE = True
except ImportError as e:
    DATABRICKS_AVAILABLE = False
    DatabricksWorkspaceManagerTool = None
    DatabricksETLNotebookGenerator = None
    print(f"Warning: Databricks modules not available: {e}")
    print(f"Ensure the following files exist:")
    print(f"  - {CUSTOM_MCP_PATH / 'Databricks_mcp.py'}")
    print(f"  - {CUSTOM_MCP_PATH / 'Databricks_ETL_Generator_mcp.py'}")


class DatabricksManager:
    """
    Central manager for all Databricks operations.
    
    This class provides a unified interface to interact with Databricks:
    - Cluster management (list, start, stop, get info)
    - Warehouse management (list, get info)
    - Notebook operations (create, read, list)
    - SQL query execution
    - ETL notebook generation from mappings
    
    Attributes:
        None (stateless wrapper around MCP functions)
    """
    
    def __init__(self):
        """Initialize the Databricks manager."""
        if not DATABRICKS_AVAILABLE:
            raise RuntimeError(
                "Databricks modules are not available. "
                "Please ensure Databricks_mcp.py and Databricks_ETL_Generator_mcp.py "
                "exist in the custom_mcp directory."
            )
    
    # ==================== Cluster Management ====================
    
    def list_clusters(self) -> Dict[str, Any]:
        """
        List all Databricks clusters in the workspace.
        
        Returns:
            Dict: Response containing list of cluster objects with details like:
                - cluster_id: Unique identifier
                - cluster_name: Human-readable name
                - state: Current state (RUNNING, TERMINATED, etc.)
                - spark_version: Spark runtime version
                - node_type_id: VM instance type
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.list_clusters()
            >>> if result['success']:
            ...     for cluster in result['data']:
            ...         print(f"{cluster['cluster_name']}: {cluster['state']}")
        """
        return DatabricksWorkspaceManagerTool(action="list_clusters")
    
    def get_cluster_info(self, cluster_name: str = None, cluster_id: str = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific cluster.
        
        Args:
            cluster_name: The name of the cluster (optional if cluster_id provided)
            cluster_id: The unique identifier of the cluster (optional if cluster_name provided)
        
        Returns:
            Dict: Detailed cluster information including configuration,
                  state, metrics, and resource allocation
        
        Example:
            >>> db = get_databricks_manager()
            >>> info = db.get_cluster_info(cluster_id="0123-456789-abc123")
            >>> print(f"Cluster: {info['data']['cluster_name']}")
        """
        return DatabricksWorkspaceManagerTool(
            action="get_cluster",
            cluster_name=cluster_name,
            cluster_id=cluster_id
        )
    
    def start_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """
        Start a terminated cluster.
        
        Args:
            cluster_id: The unique identifier of the cluster to start
        
        Returns:
            Dict: Response with status and cluster information
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.start_cluster("0123-456789-abc123")
            >>> print(f"Status: {result.get('message')}")
        """
        return DatabricksWorkspaceManagerTool(
            action="start_cluster",
            cluster_id=cluster_id
        )
    
    def stop_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """
        Stop a running cluster.
        
        Args:
            cluster_id: The unique identifier of the cluster to stop
        
        Returns:
            Dict: Response with termination status
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.stop_cluster("0123-456789-abc123")
            >>> print(f"Stopped: {result.get('message')}")
        """
        return DatabricksWorkspaceManagerTool(
            action="stop_cluster",
            cluster_id=cluster_id
        )
    
    # ==================== Warehouse Management ====================
    
    def list_warehouses(self) -> Dict[str, Any]:
        """
        List all SQL warehouses in the workspace.
        
        Returns:
            Dict: Response containing list of warehouse objects with details like:
                - id: Unique identifier
                - name: Human-readable name
                - state: Current state (RUNNING, STOPPED, etc.)
                - cluster_size: Size configuration (2X-Small, Small, etc.)
                - auto_stop_mins: Auto-stop timeout in minutes
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.list_warehouses()
            >>> if result['success']:
            ...     for wh in result['data']:
            ...         print(f"{wh['name']}: {wh['state']}")
        """
        return DatabricksWorkspaceManagerTool(action="list_warehouses")
    
    def get_warehouse_info(self, warehouse_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific SQL warehouse.
        
        Args:
            warehouse_id: The unique identifier of the warehouse
        
        Returns:
            Dict: Detailed warehouse information including configuration,
                  state, and performance settings
        
        Example:
            >>> db = get_databricks_manager()
            >>> info = db.get_warehouse_info("abc123def456")
            >>> if info['success']:
            ...     print(f"Warehouse: {info['data']['name']}, Size: {info['data']['cluster_size']}")
        """
        return DatabricksWorkspaceManagerTool(
            action="get_warehouse",
            warehouse_id=warehouse_id
        )
    
    # ==================== Notebook Operations ====================
    
    def create_notebook(
        self, 
        path: str, 
        content: str, 
        language: str = "PYTHON"
    ) -> Dict[str, Any]:
        """
        Create a new notebook in Databricks workspace.
        
        Args:
            path: Full path where notebook should be created 
                  (e.g., "/Users/user@example.com/my_notebook")
            content: Notebook content (code cells)
            language: Notebook language - PYTHON, SQL, SCALA, or R
        
        Returns:
            Dict: Response with creation status and notebook path
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.create_notebook(
            ...     path="/Users/me/test_notebook",
            ...     content="print('Hello Databricks!')",
            ...     language="PYTHON"
            ... )
            >>> print(f"Created: {result['message']}")
        """
        return DatabricksWorkspaceManagerTool(
            action="create_notebook",
            notebook_path=path,
            notebook_content=content,
            notebook_language=language
        )
    
    def list_notebooks(self, path: str = "/") -> Dict[str, Any]:
        """
        List notebooks in a specific directory.
        
        Args:
            path: Directory path to list (default: root "/")
        
        Returns:
            Dict: Response containing list of notebook objects with path, language, 
                  and object type information
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.list_notebooks("/Users/me")
            >>> if result['success']:
            ...     for nb in result['data']:
            ...         print(f"{nb['path']} ({nb.get('language', 'N/A')})")
        """
        return DatabricksWorkspaceManagerTool(
            action="list_notebooks",
            notebook_path=path
        )
    
    def list_dbfs_files(self, path: str = "/") -> Dict[str, Any]:
        """
        List files in DBFS (Databricks File System).
        
        Args:
            path: DBFS path to list (default: root "/")
        
        Returns:
            Dict: Response containing list of files and directories
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.list_dbfs_files("/FileStore")
            >>> if result['success']:
            ...     for file in result['data']:
            ...         print(f"{file['path']}")
        """
        return DatabricksWorkspaceManagerTool(
            action="list_dbfs",
            file_path=path
        )
    
    def upload_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Upload a file to DBFS.
        
        Args:
            path: DBFS path where file should be uploaded
            content: File content to upload
        
        Returns:
            Dict: Response with upload status
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.upload_file(
            ...     path="/FileStore/my_file.txt",
            ...     content="Hello DBFS!"
            ... )
            >>> print(f"Uploaded: {result['message']}")
        """
        return DatabricksWorkspaceManagerTool(
            action="upload_file",
            file_path=path,
            file_content=content
        )
    
    # ==================== SQL Query Execution ====================
    
    def execute_sql(
        self, 
        warehouse_id: str, 
        query: str
    ) -> Dict[str, Any]:
        """
        Execute a SQL query on a SQL warehouse.
        
        Args:
            warehouse_id: The ID of the warehouse to use
            query: SQL query string to execute
        
        Returns:
            Dict: Query results with columns and rows
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.execute_sql(
            ...     warehouse_id="abc123",
            ...     query="SELECT * FROM my_table LIMIT 10"
            ... )
            >>> if result['success']:
            ...     print(result['data'])
        """
        return DatabricksWorkspaceManagerTool(
            action="run_sql_query",
            warehouse_id=warehouse_id,
            sql_query=query
        )
    
    # ==================== Job Management ====================
    
    def list_jobs(self) -> Dict[str, Any]:
        """
        List all jobs in the workspace.
        
        Returns:
            Dict: Response containing list of job objects
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.list_jobs()
            >>> if result['success']:
            ...     for job in result['data']:
            ...         print(f"{job['name']} (ID: {job['job_id']})")
        """
        return DatabricksWorkspaceManagerTool(action="list_jobs")
    
    def get_job_info(self, job_name: str = None, job_id: str = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific job.
        
        Args:
            job_name: The name of the job (optional if job_id provided)
            job_id: The unique identifier of the job (optional if job_name provided)
        
        Returns:
            Dict: Detailed job information
        
        Example:
            >>> db = get_databricks_manager()
            >>> info = db.get_job_info(job_name="my-job")
            >>> if info['success']:
            ...     print(f"Job: {info['data']['name']}")
        """
        return DatabricksWorkspaceManagerTool(
            action="get_job",
            job_name=job_name,
            job_id=job_id
        )
    
    def run_job(self, job_id: str) -> Dict[str, Any]:
        """
        Trigger a job run.
        
        Args:
            job_id: The unique identifier of the job to run
        
        Returns:
            Dict: Response with run information
        
        Example:
            >>> db = get_databricks_manager()
            >>> result = db.run_job("12345")
            >>> print(f"Started run: {result['message']}")
        """
        return DatabricksWorkspaceManagerTool(
            action="run_job",
            job_id=job_id
        )
    
    # ==================== ETL Generation ====================
    
    def generate_etl_notebook(
        self,
        mappings: List[Dict[str, Any]],
        notebook_name: str = "ETL_Notebook",
        notebook_path: str = None,
        deploy_to_workspace: bool = False,
        optimization_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate a complete ETL notebook from mapping specifications.
        
        Args:
            mappings: List of field mappings with structure:
                [
                    {
                        "mapping_name": "Transform_Name",
                        "mapping_complexity": "Simple" | "Medium" | "Complex",
                        "source_name": "Source_System_Name",
                        "target_name": "Target_System_Name",
                        "source_type": "CSV" | "Parquet" | "Delta" | "JDBC" | "JSON",
                        "target_type": "Delta" | "Parquet" | "CSV" | "JDBC",
                        "source_object": "table_name or file_path",
                        "source_field": "column_name",
                        "transformation_logic": "CAST AS STRING, TRIM, UPPER",
                        "target_object": "target_table_name",
                        "target_field": "target_column_name"
                    },
                    ...
                ]
            notebook_name: Name for the generated notebook (default: "ETL_Notebook")
            notebook_path: Workspace path to deploy (e.g., "/Users/user@example.com/ETL")
            deploy_to_workspace: If True, deploy directly to Databricks workspace
            optimization_level: "standard", "advanced", or "maximum"
        
        Returns:
            Dict: Response with generated notebook code and metadata
        
        Example:
            >>> db = get_databricks_manager()
            >>> mappings = [
            ...     {
            ...         "mapping_name": "Customer_ID_Transform",
            ...         "mapping_complexity": "Simple",
            ...         "source_name": "CRM_Database",
            ...         "target_name": "Analytics_Warehouse",
            ...         "source_type": "CSV",
            ...         "target_type": "Delta",
            ...         "source_object": "/data/customers.csv",
            ...         "source_field": "customer_id",
            ...         "transformation_logic": "CAST AS STRING, TRIM",
            ...         "target_object": "dim_customer",
            ...         "target_field": "customer_key"
            ...     }
            ... ]
            >>> result = db.generate_etl_notebook(mappings, notebook_name="Customer_ETL")
            >>> if result['success']:
            ...     print(f"Generated notebook code")
        """
        return DatabricksETLNotebookGenerator(
            mappings=mappings,
            notebook_name=notebook_name,
            notebook_path=notebook_path,
            deploy_to_workspace=deploy_to_workspace,
            optimization_level=optimization_level
        )
    
    def get_help(self) -> Dict[str, Any]:
        """
        Get usage instructions and help for Databricks operations.
        
        Returns:
            Dict: Help information and usage guide
        
        Example:
            >>> db = get_databricks_manager()
            >>> help_info = db.get_help()
            >>> print(help_info['message'])
        """
        return DatabricksWorkspaceManagerTool(action="help")


# ==================== Singleton Pattern ====================

_databricks_manager: Optional[DatabricksManager] = None

def get_databricks_manager() -> DatabricksManager:
    """
    Get or create the Databricks manager singleton instance.
    
    This function ensures only one DatabricksManager instance exists
    throughout the application lifecycle, preventing redundant
    initializations and ensuring consistent state.
    
    Returns:
        DatabricksManager: The singleton manager instance
    
    Example:
        >>> from backend.src.tools.databricks_integration import get_databricks_manager
        >>> db = get_databricks_manager()
        >>> clusters = db.list_clusters()
    """
    global _databricks_manager
    if _databricks_manager is None:
        _databricks_manager = DatabricksManager()
    return _databricks_manager


def reset_databricks_manager():
    """
    Reset the singleton instance (useful for testing).
    
    Example:
        >>> from backend.src.tools.databricks_integration import reset_databricks_manager
        >>> reset_databricks_manager()  # Force new instance on next get
    """
    global _databricks_manager
    _databricks_manager = None


# ==================== Module-level Exports ====================

__all__ = [
    'DatabricksManager',
    'get_databricks_manager',
    'reset_databricks_manager',
    'DATABRICKS_AVAILABLE'
]
