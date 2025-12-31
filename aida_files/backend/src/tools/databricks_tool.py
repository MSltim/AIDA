"""
Databricks Tool for AIDA Agents
Provides Databricks operations that can be used by any agent in the AIDA system
"""
from typing import Dict, Any, List
from backend.src.tools.databricks_integration import get_databricks_manager


class DatabricksTool:
    """
    Databricks operations tool for AIDA agents.
    
    This tool provides access to Databricks clusters, warehouses, notebooks,
    and ETL generation capabilities.
    """
    
    def __init__(self):
        self.db = get_databricks_manager()
    
    def list_clusters(self) -> Dict[str, Any]:
        """
        List all available Databricks clusters.
        
        Returns:
            Dict with success status and cluster data
        """
        return self.db.list_clusters()
    
    def list_warehouses(self) -> Dict[str, Any]:
        """
        List all SQL warehouses.
        
        Returns:
            Dict with success status and warehouse data
        """
        return self.db.list_warehouses()
    
    def create_notebook(self, path: str, content: str, language: str = "PYTHON") -> Dict[str, Any]:
        """
        Create a new Databricks notebook.
        
        Args:
            path: Notebook path (e.g., "/Users/user@example.com/my_notebook")
            content: Notebook code content
            language: Programming language (PYTHON, SQL, SCALA, R)
        
        Returns:
            Dict with creation status and notebook info
        """
        return self.db.create_notebook(path, content, language)
    
    def execute_sql(self, warehouse_id: str, query: str) -> Dict[str, Any]:
        """
        Execute SQL query on a warehouse.
        
        Args:
            warehouse_id: ID of the SQL warehouse
            query: SQL query to execute
        
        Returns:
            Dict with query results
        """
        return self.db.execute_sql(warehouse_id, query)
    
    def generate_etl_notebook(
        self,
        mappings: List[Dict[str, Any]],
        source_objects: List[Dict[str, Any]],
        target_objects: List[Dict[str, Any]],
        notebook_name: str = "Generated_ETL"
    ) -> Dict[str, Any]:
        """
        Generate ETL notebook from mappings.
        
        Args:
            mappings: Field mapping definitions
            source_objects: Source table/file definitions
            target_objects: Target table definitions
            notebook_name: Name for generated notebook
        
        Returns:
            Dict with generated notebook code
        """
        return self.db.generate_etl_notebook(
            mappings=mappings,
            source_objects=source_objects,
            target_objects=target_objects,
            notebook_name=notebook_name
        )


# Singleton instance
_databricks_tool = None

def get_databricks_tool():
    """Get or create the Databricks tool instance"""
    global _databricks_tool
    if _databricks_tool is None:
        _databricks_tool = DatabricksTool()
    return _databricks_tool


# Example usage functions for agents
def databricks_list_clusters_tool():
    """Agent tool function to list Databricks clusters"""
    tool = get_databricks_tool()
    return tool.list_clusters()


def databricks_list_warehouses_tool():
    """Agent tool function to list SQL warehouses"""
    tool = get_databricks_tool()
    return tool.list_warehouses()


def databricks_create_notebook_tool(path: str, content: str, language: str = "PYTHON"):
    """Agent tool function to create Databricks notebook"""
    tool = get_databricks_tool()
    return tool.create_notebook(path, content, language)


def databricks_execute_sql_tool(warehouse_id: str, query: str):
    """Agent tool function to execute SQL"""
    tool = get_databricks_tool()
    return tool.execute_sql(warehouse_id, query)
