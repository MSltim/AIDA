"""
Databricks ETL Generation Use Case
Demonstrates how to use Databricks integration in a standalone script
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.tools.databricks_integration import get_databricks_manager


def example_1_list_resources():
    """Example 1: List Databricks resources"""
    print("\n" + "="*70)
    print("EXAMPLE 1: List Databricks Resources")
    print("="*70)
    
    db = get_databricks_manager()
    
    # List clusters
    print("\n📊 Listing Clusters...")
    result = db.list_clusters()
    if result['success']:
        clusters = result['data'].get('clusters', [])
        print(f"Found {len(clusters)} clusters:")
        for cluster in clusters:
            print(f"  - {cluster.get('cluster_name')} ({cluster.get('state')})")
    else:
        print(f"Error: {result.get('message')}")
    
    # List warehouses
    print("\n🏢 Listing SQL Warehouses...")
    result = db.list_warehouses()
    if result['success']:
        warehouses = result['data'].get('warehouses', [])
        print(f"Found {len(warehouses)} warehouses:")
        for wh in warehouses:
            print(f"  - {wh.get('name')} ({wh.get('state')})")
    else:
        print(f"Error: {result.get('message')}")


def example_2_create_simple_notebook():
    """Example 2: Create a simple analysis notebook"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Create Analysis Notebook")
    print("="*70)
    
    db = get_databricks_manager()
    
    notebook_code = """
# MAGIC %md
# MAGIC # Sales Data Analysis
# MAGIC This notebook performs basic sales analysis

# Import libraries
from pyspark.sql.functions import *

# Read data
sales_df = spark.read.format("delta").load("/mnt/data/sales")

# Show sample
print("Sample data:")
sales_df.show(5)

# Calculate metrics
total_sales = sales_df.agg(sum("amount").alias("total")).collect()[0]["total"]
print(f"Total Sales: ${total_sales:,.2f}")

# Group by product
product_sales = sales_df.groupBy("product") \\
    .agg(
        sum("amount").alias("revenue"),
        count("*").alias("transactions")
    ) \\
    .orderBy(desc("revenue"))

print("Top Products:")
product_sales.show(10)
"""
    
    print("\n📝 Generated notebook code (not deploying to workspace):")
    print("   Lines of code:", len(notebook_code.splitlines()))
    print("\n   To deploy to your workspace, use a valid path like:")
    print("   - /Users/your.email@company.com/sales_analysis")
    print("   - /Workspace/Users/your.email@company.com/sales_analysis")
    print("   - /Shared/team_folder/sales_analysis")
    
    # Show how to deploy if user wants to
    print("\n💡 To deploy to Databricks workspace:")
    print("   Replace 'your.email@company.com' with your actual email:")
    print("   ")
    print("   result = db.create_notebook(")
    print("       path='/Users/your.email@company.com/sales_analysis',")
    print("       content=notebook_code,")
    print("       language='PYTHON'")
    print("   )")
    
    # Save locally as demonstration
    local_file = "sales_analysis_notebook.py"
    with open(local_file, 'w', encoding='utf-8') as f:
        f.write(notebook_code)
    print(f"\n   💾 Saved notebook code to: {local_file}")
    print("   ✅ You can manually import this file to Databricks UI")


def example_3_generate_etl_notebook():
    """Example 3: Generate ETL notebook from mappings"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Generate Customer ETL Notebook")
    print("="*70)
    
    db = get_databricks_manager()
    
    # Define mappings using the correct format
    mappings = [
        {
            "mapping_name": "Customer_ID_Transform",
            "mapping_complexity": "Simple",
            "source_name": "CRM_Database",
            "target_name": "Analytics_Warehouse",
            "source_type": "CSV",
            "target_type": "Delta",
            "source_object": "/mnt/raw/customers/customer_data.csv",
            "source_field": "customer_id",
            "transformation_logic": "CAST AS STRING, TRIM",
            "target_object": "dim_customer",
            "target_field": "customer_key"
        },
        {
            "mapping_name": "Customer_FirstName",
            "mapping_complexity": "Simple",
            "source_name": "CRM_Database",
            "target_name": "Analytics_Warehouse",
            "source_type": "CSV",
            "target_type": "Delta",
            "source_object": "/mnt/raw/customers/customer_data.csv",
            "source_field": "first_name",
            "transformation_logic": "TRIM, UPPER",
            "target_object": "dim_customer",
            "target_field": "first_name"
        },
        {
            "mapping_name": "Customer_LastName",
            "mapping_complexity": "Simple",
            "source_name": "CRM_Database",
            "target_name": "Analytics_Warehouse",
            "source_type": "CSV",
            "target_type": "Delta",
            "source_object": "/mnt/raw/customers/customer_data.csv",
            "source_field": "last_name",
            "transformation_logic": "TRIM, UPPER",
            "target_object": "dim_customer",
            "target_field": "last_name"
        },
        {
            "mapping_name": "Customer_Email",
            "mapping_complexity": "Medium",
            "source_name": "CRM_Database",
            "target_name": "Analytics_Warehouse",
            "source_type": "CSV",
            "target_type": "Delta",
            "source_object": "/mnt/raw/customers/customer_data.csv",
            "source_field": "email",
            "transformation_logic": "LOWER, TRIM",
            "target_object": "dim_customer",
            "target_field": "email_address"
        },
        {
            "mapping_name": "Customer_Phone",
            "mapping_complexity": "Simple",
            "source_name": "CRM_Database",
            "target_name": "Analytics_Warehouse",
            "source_type": "CSV",
            "target_type": "Delta",
            "source_object": "/mnt/raw/customers/customer_data.csv",
            "source_field": "phone",
            "transformation_logic": "TRIM",
            "target_object": "dim_customer",
            "target_field": "phone_number"
        },
        {
            "mapping_name": "Customer_CreatedDate",
            "mapping_complexity": "Medium",
            "source_name": "CRM_Database",
            "target_name": "Analytics_Warehouse",
            "source_type": "CSV",
            "target_type": "Delta",
            "source_object": "/mnt/raw/customers/customer_data.csv",
            "source_field": "created_date",
            "transformation_logic": "TO_DATE",
            "target_object": "dim_customer",
            "target_field": "customer_since_date"
        }
    ]
    
    # Generate ETL notebook
    print("\n🔄 Generating ETL notebook with 6 field mappings...")
    result = db.generate_etl_notebook(
        mappings=mappings,
        notebook_name="Customer_Dimension_ETL",
        optimization_level="standard"
    )
    
    if result.get('success'):
        notebook_code = result.get('notebook_code', '')
        print(f"✅ ETL Notebook generated successfully!")
        print(f"   Lines of code: {len(notebook_code.splitlines())}")
        print(f"\n   Preview (first 800 characters):")
        print("   " + "-"*66)
        print("   " + notebook_code[:800].replace('\n', '\n   '))
        print("   " + "-"*66)
        
        # Optionally save to file
        output_file = "generated_customer_etl.py"
        with open(output_file, 'w') as f:
            f.write(notebook_code)
        print(f"\n   💾 Saved complete notebook to: {output_file}")
    else:
        print(f"❌ Error: {result.get('message', result.get('error', 'Unknown error'))}")


def example_4_execute_sql_query():
    """Example 4: Execute SQL query on warehouse"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Execute SQL Query")
    print("="*70)
    
    db = get_databricks_manager()
    
    # First, get available warehouses
    wh_result = db.list_warehouses()
    if not wh_result['success']:
        print("❌ Cannot list warehouses")
        return
    
    warehouses = wh_result['data'].get('warehouses', [])
    if not warehouses:
        print("⚠️  No warehouses available")
        return
    
    warehouse_id = warehouses[0]['id']
    print(f"📊 Using warehouse: {warehouses[0]['name']}")
    
    # Execute a query
    query = """
    SELECT 
        date_format(current_date(), 'yyyy-MM-dd') as query_date,
        'AIDA' as system_name,
        'Databricks Integration Test' as description
    """
    
    print(f"\n🔍 Executing query...")
    result = db.execute_sql(warehouse_id, query)
    
    if result.get('success'):
        print("✅ Query executed successfully!")
        # Parse results if available
        if 'data' in result:
            print(f"   Results: {result['data']}")
    else:
        print(f"❌ Error: {result.get('message')}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  DATABRICKS INTEGRATION - USE CASE EXAMPLES")
    print("="*70)
    print("\n  Demonstrating various ways to use Databricks integration")
    print("  in your AIDA application\n")
    
    try:
        # Run examples
        example_1_list_resources()
        example_2_create_simple_notebook()
        example_3_generate_etl_notebook()
        example_4_execute_sql_query()
        
        print("\n" + "="*70)
        print("  ✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\n  You can now use these patterns in:")
        print("    - Your agents (backend/src/agents/)")
        print("    - Use cases (backend/src/usecase/)")
        print("    - Tools (backend/src/tools/)")
        print("    - API endpoints (if you have a FastAPI backend)")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
