"""
Data Engineering Agent
Specialized agent for Databricks ETL operations and data pipeline management
"""
from typing import List, Any, Dict
from backend.src.tools.databricks_integration import get_databricks_manager


async def DataEngineeringAgent(
    provider: str, 
    model_name: str, 
    temperature: float, 
    tools: List[Any] = None
) -> Any:
    """
    Data Engineering Agent that can:
    - Generate ETL notebooks from specifications
    - Manage Databricks clusters and warehouses
    - Execute data quality queries
    - Monitor data pipelines
    
    Args:
        provider: LLM provider (e.g., "azure_openai")
        model_name: Model name to use
        temperature: Temperature for generation
        tools: Additional tools to provide
    
    Returns:
        Configured agent instance
    """
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import AzureChatOpenAI
    
    # Initialize Databricks manager
    db = get_databricks_manager()
    
    # Create Databricks-specific tools
    databricks_tools = create_databricks_tools(db)
    
    # Combine with any additional tools
    all_tools = databricks_tools + (tools or [])
    
    # Initialize LLM
    llm = AzureChatOpenAI(
        model=model_name,
        temperature=temperature,
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    
    # System prompt for data engineering
    system_prompt = """You are a Data Engineering specialist with expertise in:
- Databricks ETL development
- PySpark and SQL optimization
- Data pipeline architecture
- Data quality and validation

When asked to create ETL processes:
1. Understand the source and target specifications
2. Generate optimized PySpark/SQL code
3. Include error handling and logging
4. Add data quality checks
5. Create Databricks notebooks with proper structure

Available Databricks operations:
- List and manage clusters
- Create notebooks
- Execute SQL queries
- Generate ETL notebooks from mappings
"""
    
    # Create and return agent
    agent = create_react_agent(
        llm,
        tools=all_tools,
        state_modifier=system_prompt
    )
    
    return agent


def create_databricks_tools(db_manager):
    """Create LangChain tools from Databricks manager"""
    from langchain_core.tools import tool
    
    @tool
    def list_databricks_clusters() -> Dict[str, Any]:
        """List all Databricks clusters in the workspace"""
        return db_manager.list_clusters()
    
    @tool
    def list_databricks_warehouses() -> Dict[str, Any]:
        """List all SQL warehouses"""
        return db_manager.list_warehouses()
    
    @tool
    def create_databricks_notebook(
        path: str,
        content: str,
        language: str = "PYTHON"
    ) -> Dict[str, Any]:
        """
        Create a new Databricks notebook.
        
        Args:
            path: Full notebook path like "/Users/user@example.com/my_notebook"
            content: Notebook code content
            language: PYTHON, SQL, SCALA, or R
        """
        return db_manager.create_notebook(path, content, language)
    
    @tool
    def execute_databricks_sql(warehouse_id: str, query: str) -> Dict[str, Any]:
        """
        Execute SQL query on a Databricks SQL warehouse.
        
        Args:
            warehouse_id: The warehouse ID to use
            query: SQL query to execute
        """
        return db_manager.execute_sql(warehouse_id, query)
    
    @tool
    def generate_databricks_etl(
        source_name: str,
        source_type: str,
        source_path: str,
        target_name: str,
        target_type: str,
        target_path: str,
        field_mappings: str,
        notebook_name: str = "Generated_ETL"
    ) -> Dict[str, Any]:
        """
        Generate a complete ETL notebook from specifications.
        
        Args:
            source_name: Name of source (e.g., "customers_csv")
            source_type: Type of source (csv, json, delta, parquet)
            source_path: Path to source data
            target_name: Name of target (e.g., "customer_dim")
            target_type: Type of target (delta, csv, parquet)
            target_path: Path where to write target
            field_mappings: JSON string of field mappings
            notebook_name: Name for the generated notebook
        
        Example field_mappings:
        [
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
        """
        import json
        
        # Parse field mappings
        try:
            mappings = json.loads(field_mappings)
        except:
            return {
                "success": False,
                "error": "Invalid field_mappings JSON format"
            }
        
        # Construct source and target objects
        source_objects = [{
            "name": source_name,
            "type": source_type,
            "path": source_path
        }]
        
        target_objects = [{
            "name": target_name,
            "type": target_type,
            "path": target_path,
            "mode": "overwrite"
        }]
        
        return db_manager.generate_etl_notebook(
            mappings=mappings,
            source_objects=source_objects,
            target_objects=target_objects,
            notebook_name=notebook_name
        )
    
    return [
        list_databricks_clusters,
        list_databricks_warehouses,
        create_databricks_notebook,
        execute_databricks_sql,
        generate_databricks_etl
    ]


# Example usage
if __name__ == "__main__":
    import asyncio
    import os
    
    async def demo():
        """Demo the Data Engineering Agent"""
        
        # Create agent
        agent = await DataEngineeringAgent(
            provider="azure_openai",
            model_name="gpt-4o-ReCast",
            temperature=0.1
        )
        
        # Example queries
        queries = [
            "List all my Databricks clusters",
            "Show me the SQL warehouses",
            "Generate an ETL notebook that reads from /data/customers.csv and writes to delta table /delta/customer_dim"
        ]
        
        for query in queries:
            print(f"\n{'='*70}")
            print(f"Query: {query}")
            print(f"{'='*70}")
            
            result = await agent.ainvoke({"messages": [("user", query)]})
            print(result)
    
    # Run demo
    # asyncio.run(demo())
