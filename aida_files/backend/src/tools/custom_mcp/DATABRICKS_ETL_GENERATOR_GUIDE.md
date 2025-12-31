# Databricks ETL Notebook Generator - Complete Guide

## Overview
The Databricks ETL Notebook Generator is a specialized MCP tool that automatically creates production-ready, parameterized PySpark notebooks based on client-provided ETL mapping specifications. It handles complex transformations, multiple source/target types, validation, and optimization.

## Features
- **Auto-generates complete PySpark notebooks** from mapping specifications
- **Supports multiple data sources**: CSV, Parquet, Delta, JSON, JDBC
- **Supports multiple targets**: Delta, Parquet, CSV, JDBC  
- **Built-in transformations**: TRIM, UPPER, LOWER, CAST, SUBSTRING, HASH, REPLACE, etc.
- **Parameterized with dbutils.widgets** for easy reusability
- **Data quality validation** with automated checks
- **Audit columns** automatically added
- **Optimization hints** and best practices included
- **Direct deployment** to Databricks workspace

---

## Mapping Specification Format

### Required Fields

Each mapping must contain these fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `mapping_name` | string | Unique identifier for mapping | "Customer_ID_Transform" |
| `mapping_complexity` | string | Simple/Medium/Complex | "Medium" |
| `source_name` | string | Logical source system name | "CRM_Database" |
| `target_name` | string | Logical target system name | "Analytics_DW" |
| `source_type` | string | CSV/Parquet/Delta/JDBC/JSON | "JDBC" |
| `target_type` | string | Delta/Parquet/CSV/JDBC | "Delta" |
| `source_object` | string | Source table/file path | "customers" |
| `source_field` | string | Source column name | "customer_id" |
| `transformation_logic` | string | Comma-separated transforms | "CAST AS STRING, TRIM, UPPER" |
| `target_object` | string | Target table/file path | "dim_customer" |
| `target_field` | string | Target column name | "customer_key" |

### Sample Mapping

```python
{
    "mapping_name": "Customer_Key_Transform",
    "mapping_complexity": "Medium",
    "source_name": "CRM_DB",
    "target_name": "Analytics_DW",
    "source_type": "JDBC",
    "target_type": "Delta",
    "source_object": "customers",
    "source_field": "customer_id",
    "transformation_logic": "CAST AS STRING, TRIM, UPPER",
    "target_object": "dim_customer",
    "target_field": "customer_key"
}
```

---

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install python-dotenv mcp requests
```

### Step 2: Configure Environment

Add to your `.env` file:

```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi1234567890abcdef...
```

### Step 3: Configure MCP

Edit your `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "databricks-etl-generator": {
      "command": "C:\\AiCOE\\AIDA\\AIDA\\Scripts\\python.exe",
      "args": [
        "C:\\AiCOE\\AIDA\\backend\\src\\tools\\custom_mcp\\Databricks_ETL_Generator_mcp.py"
      ],
      "env": {
        "DATABRICKS_HOST": "your-workspace-url",
        "DATABRICKS_TOKEN": "your-token"
      }
    }
  }
}
```

### Step 4: Reload VS Code

Press `Ctrl+Shift+P` → "Reload Window"

---

## Usage Examples

### Example 1: Simple Customer Dimension ETL

```python
from Databricks_ETL_Generator_mcp import DatabricksETLNotebookGenerator

# Define mappings
mappings = [
    {
        "mapping_name": "Customer_ID",
        "mapping_complexity": "Simple",
        "source_name": "CRM",
        "target_name": "DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "crm_customers.csv",
        "source_field": "id",
        "transformation_logic": "CAST AS STRING, TRIM",
        "target_object": "dim_customer",
        "target_field": "customer_key"
    },
    {
        "mapping_name": "Customer_Name",
        "mapping_complexity": "Simple",
        "source_name": "CRM",
        "target_name": "DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "crm_customers.csv",
        "source_field": "full_name",
        "transformation_logic": "TRIM, INITCAP",
        "target_object": "dim_customer",
        "target_field": "customer_name"
    },
    {
        "mapping_name": "Customer_Email",
        "mapping_complexity": "Medium",
        "source_name": "CRM",
        "target_name": "DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "crm_customers.csv",
        "source_field": "email",
        "transformation_logic": "TRIM, LOWER",
        "target_object": "dim_customer",
        "target_field": "email_address"
    }
]

# Generate notebook (preview only)
result = DatabricksETLNotebookGenerator(
    mappings=mappings,
    notebook_name="Customer_Dimension_ETL",
    optimization_level="standard"
)

# Print generated code
print(result["data"]["notebook_code"])

# Save to file
with open("Customer_ETL.py", "w") as f:
    f.write(result["data"]["notebook_code"])
```

### Example 2: Complex JDBC to Delta Pipeline

```python
mappings = [
    {
        "mapping_name": "Order_ID",
        "mapping_complexity": "Simple",
        "source_name": "ERP_System",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "order_id",
        "transformation_logic": "CAST AS STRING",
        "target_object": "fact_orders",
        "target_field": "order_key"
    },
    {
        "mapping_name": "Order_Date",
        "mapping_complexity": "Simple",
        "source_name": "ERP_System",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "order_date",
        "transformation_logic": "CAST AS DATE",
        "target_object": "fact_orders",
        "target_field": "order_date"
    },
    {
        "mapping_name": "Customer_ID_Masked",
        "mapping_complexity": "Complex",
        "source_name": "ERP_System",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "customer_id",
        "transformation_logic": "CAST AS STRING, SHA256",
        "target_object": "fact_orders",
        "target_field": "customer_key_masked"
    },
    {
        "mapping_name": "Order_Amount",
        "mapping_complexity": "Medium",
        "source_name": "ERP_System",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "total_amount",
        "transformation_logic": "CAST AS DOUBLE, COALESCE_NULL",
        "target_object": "fact_orders",
        "target_field": "order_amount"
    }
]

# Generate and deploy to workspace
result = DatabricksETLNotebookGenerator(
    mappings=mappings,
    notebook_name="Orders_ETL_Pipeline",
    notebook_path="/Users/data.engineer@company.com/ETL/Orders_Pipeline",
    deploy_to_workspace=True,
    optimization_level="advanced"
)

if result["success"]:
    print(f"✓ Notebook deployed: {result['deployment']['notebook_url']}")
```

### Example 3: Multi-Source Aggregation

```python
# Sales data from CSV
sales_mappings = [
    {
        "mapping_name": "Sales_ID",
        "mapping_complexity": "Simple",
        "source_name": "Sales_Files",
        "target_name": "Analytics",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "daily_sales.csv",
        "source_field": "sale_id",
        "transformation_logic": "CAST AS STRING, TRIM",
        "target_object": "fact_sales",
        "target_field": "sales_key"
    },
    {
        "mapping_name": "Sales_Amount",
        "mapping_complexity": "Simple",
        "source_name": "Sales_Files",
        "target_name": "Analytics",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "daily_sales.csv",
        "source_field": "amount",
        "transformation_logic": "CAST AS DOUBLE",
        "target_object": "fact_sales",
        "target_field": "sale_amount"
    },
    {
        "mapping_name": "Product_Code",
        "mapping_complexity": "Medium",
        "source_name": "Sales_Files",
        "target_name": "Analytics",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "daily_sales.csv",
        "source_field": "product_cd",
        "transformation_logic": "TRIM, UPPER, REPLACE(' ','')",
        "target_object": "fact_sales",
        "target_field": "product_code"
    }
]

result = DatabricksETLNotebookGenerator(
    mappings=sales_mappings,
    notebook_name="Daily_Sales_ETL",
    notebook_path="/Shared/ETL/Sales",
    deploy_to_workspace=True,
    optimization_level="maximum"
)
```

---

## Supported Transformations

### String Transformations
| Transformation | Description | Example |
|----------------|-------------|---------|
| `TRIM` | Remove leading/trailing spaces | "  ABC  " → "ABC" |
| `UPPER` | Convert to uppercase | "abc" → "ABC" |
| `LOWER` | Convert to lowercase | "ABC" → "abc" |
| `INITCAP` | Capitalize first letter of each word | "john doe" → "John Doe" |
| `SUBSTRING(start,length)` | Extract substring | "ABCDEF", SUBSTRING(1,3) → "ABC" |
| `REPLACE('old','new')` | Replace text | REPLACE('Mr.','') |

### Type Conversions
| Transformation | Description |
|----------------|-------------|
| `CAST AS STRING` | Convert to string |
| `CAST AS INTEGER` | Convert to integer |
| `CAST AS LONG` | Convert to long |
| `CAST AS DOUBLE` | Convert to double/float |
| `CAST AS DATE` | Convert to date |
| `CAST AS TIMESTAMP` | Convert to timestamp |

### Security/Privacy
| Transformation | Description |
|----------------|-------------|
| `HASH` or `MD5` | MD5 hash |
| `SHA256` | SHA-256 hash |

### Data Quality
| Transformation | Description |
|----------------|-------------|
| `COALESCE_NULL` | Replace nulls with empty string |

### Combining Transformations

Transformations can be chained with commas:

```python
"transformation_logic": "TRIM, UPPER, CAST AS STRING, REPLACE('-','')"
```

Execution order: left to right

---

## Using with AI Assistant

Once configured, simply provide mappings in natural language:

### Example Conversation 1
**You:** "Generate a Databricks ETL notebook for customer data. Map customer_id from CSV to customer_key in Delta table. Apply TRIM and UPPER transformations."

**AI Will:**
1. Extract mapping details
2. Call `DatabricksETLNotebookGenerator`
3. Return generated notebook code
4. Optionally deploy to workspace

### Example Conversation 2
**You:** "I have this Excel file with mappings: [paste mapping data]. Create the ETL notebook."

**AI Will:**
1. Parse the mapping data
2. Convert to proper format
3. Generate notebook
4. Show summary and deployment options

### Example Conversation 3
**You:** "Generate ETL for:
- Source: orders table (JDBC)
- Target: fact_orders (Delta)
- Fields: order_id → order_key, customer_id → customer_key (hash it), amount → order_amount
Deploy to /Users/me/ETL/Orders"

**AI Will:**
1. Build mappings from description
2. Generate complete notebook
3. Deploy to specified path
4. Provide notebook URL

---

## Generated Notebook Structure

The generated notebooks follow this structure:

### 1. Header & Documentation
- Notebook title and purpose
- Mapping summary
- Source/target information

### 2. Setup & Configuration
- Library imports
- Spark session initialization
- Optimization settings

### 3. Parameter Widgets
- Source paths/connections
- Target paths/connections
- Write mode (overwrite/append/merge)
- Validation toggle
- Secret scope configuration

### 4. Helper Functions
- `log_message()` - Standardized logging
- `validate_dataframe()` - Data quality checks
- `apply_transformations()` - Transform engine

### 5. Source Data Reading
- Read from each source object
- Schema enforcement
- Initial validation

### 6. Transformations
- Field-level transformations
- Data type conversions
- Business logic application
- Audit column addition

### 7. Data Quality Validation
- Row count checks
- Null value detection
- Duplicate checking
- Schema validation

### 8. Target Writing
- Write to target objects
- Mode handling (overwrite/append/merge)
- Error handling

### 9. Summary & Statistics
- Execution summary
- Record counts
- Success/failure status

### 10. Documentation Section
- Cluster configuration recommendations
- Performance optimization tips
- Monitoring guidelines
- Security best practices

---

## Output Example

```json
{
  "success": true,
  "data": {
    "notebook_name": "Customer_ETL",
    "notebook_code": "# Databricks notebook source\n...",
    "total_mappings": 5,
    "source_objects": ["customers", "addresses"],
    "target_objects": ["dim_customer"],
    "complexity_distribution": {
      "Simple": 3,
      "Medium": 2
    }
  },
  "deployment": {
    "success": true,
    "message": "Notebook deployed successfully to /Users/...",
    "notebook_url": "https://workspace.databricks.com/#notebook/..."
  },
  "message": "Successfully generated ETL notebook with 5 mappings"
}
```

---

## Optimization Levels

### Standard (Default)
- Basic Spark optimizations
- Adaptive query execution
- Automatic partition coalescing

### Advanced
- All standard optimizations
- Skew join handling
- Delta optimize write
- Auto compaction

### Maximum
- All advanced optimizations
- Aggressive caching recommendations
- Z-ordering suggestions
- Partition pruning

---

## Best Practices

### 1. Mapping Organization
- Group related mappings together
- Use consistent naming conventions
- Document complex transformation logic
- Include mapping version in notebook name

### 2. Source/Target Configuration
- Use meaningful object names
- Standardize path conventions
- Document JDBC connection requirements
- Specify partition columns for large tables

### 3. Transformation Logic
- Keep transformations simple and testable
- Chain multiple transforms when needed
- Document custom transformation requirements
- Use consistent date/time formats

### 4. Performance Optimization
- Partition large Delta tables by date
- Use broadcast joins for small dimensions
- Cache frequently reused DataFrames
- Monitor Spark UI for bottlenecks

### 5. Data Quality
- Always enable validation in production
- Set up alerts for data quality failures
- Document expected value ranges
- Implement row-level error handling

### 6. Security
- Store credentials in secret scopes
- Never hardcode passwords
- Use service principals for production
- Implement column-level encryption if needed

---

## Cluster Configuration

### Development
```
Workers: 2
Node Type: Standard_DS3_v2
Runtime: DBR 12.2 LTS
Auto-scaling: Disabled
```

### Production
```
Workers: 4-16 (auto-scaling)
Node Type: Standard_DS4_v2 or higher
Runtime: DBR 12.2 LTS or newer
Auto-scaling: Enabled
Spot instances: Consider for cost savings
```

---

## Troubleshooting

### Issue 1: Notebook Generation Fails
**Error:** "Missing required fields in mapping"

**Solution:**
- Verify all required fields are present
- Check field names match exactly
- Ensure no null/empty values

### Issue 2: Deployment Failed
**Error:** "Failed to deploy notebook to workspace"

**Solution:**
- Verify DATABRICKS_HOST and DATABRICKS_TOKEN
- Check notebook_path is valid
- Ensure you have write permissions
- Verify workspace path exists

### Issue 3: Generated Notebook Fails to Run
**Error:** "Column not found" or "Table not found"

**Solution:**
- Check source_field names match actual data
- Verify source_object paths are correct
- Update widget default values
- Review transformation logic syntax

### Issue 4: Performance Issues
**Symptom:** Slow execution times

**Solution:**
- Increase cluster size
- Enable auto-scaling
- Add partition columns
- Review Spark UI for bottlenecks
- Consider caching intermediate results

### Issue 5: Validation Errors
**Error:** Data quality validation failures

**Solution:**
- Review null value handling
- Check data type conversions
- Verify transformation logic
- Implement error handling/logging

---

## API Reference

### DatabricksETLNotebookGenerator

```python
def DatabricksETLNotebookGenerator(
    mappings: List[Dict],
    notebook_name: str = "ETL_Notebook",
    notebook_path: str = None,
    deploy_to_workspace: bool = False,
    optimization_level: str = "standard"
) -> dict
```

**Parameters:**
- `mappings` (List[Dict], required): List of mapping specifications
- `notebook_name` (str, optional): Name for generated notebook
- `notebook_path` (str, optional): Workspace deployment path
- `deploy_to_workspace` (bool, optional): Deploy to workspace immediately
- `optimization_level` (str, optional): "standard", "advanced", or "maximum"

**Returns:**
Dictionary with:
- `success` (bool): Operation success status
- `data` (dict): Notebook code and metadata
- `deployment` (dict): Deployment results if deployed
- `message` (str): Human-readable message

---

## Advanced Scenarios

### Scenario 1: Incremental Loads

Add watermark column to mappings:

```python
{
    "mapping_name": "Modified_Date",
    "source_field": "last_modified_dt",
    "transformation_logic": "CAST AS TIMESTAMP",
    "target_field": "modified_timestamp"
}
```

Then use in notebook:
```python
# Add incremental load logic
last_load_date = spark.sql("SELECT MAX(modified_timestamp) FROM target_table").collect()[0][0]
df_incremental = df_source.filter(col("modified_timestamp") > last_load_date)
```

### Scenario 2: SCD Type 2 Implementation

Generate base notebook, then enhance with SCD logic:

```python
# In generated notebook, add SCD Type 2 merge
from delta.tables import *

deltaTable = DeltaTable.forPath(spark, target_path)

deltaTable.alias("target").merge(
    df_transformed.alias("source"),
    "target.customer_key = source.customer_key AND target.is_current = true"
).whenMatchedUpdate(
    condition = "target.hash_value != source.hash_value",
    set = {
        "is_current": "false",
        "end_date": "current_date()"
    }
).whenNotMatchedInsert(
    values = {
        "customer_key": "source.customer_key",
        "is_current": "true",
        "start_date": "current_date()"
    }
).execute()
```

### Scenario 3: Data Masking for Different Environments

Use environment-specific transformations:

```python
# Development: Hash sensitive fields
"transformation_logic": "SHA256"

# Production: Keep original but encrypt
"transformation_logic": "ENCRYPT_AES256"  # Custom UDF
```

---

## Integration with CI/CD

### 1. Version Control
```bash
# Store generated notebooks in Git
git add notebooks/ETL/Customer_ETL_v1.py
git commit -m "Generated Customer ETL notebook"
git push
```

### 2. Automated Testing
```python
# Create test mappings
test_mappings = load_test_mappings()

# Generate notebook
result = DatabricksETLNotebookGenerator(
    mappings=test_mappings,
    notebook_name="Test_ETL"
)

# Validate generated code
assert result["success"]
assert "def log_message" in result["data"]["notebook_code"]
```

### 3. Deployment Pipeline
```yaml
# Azure DevOps / GitHub Actions
steps:
  - name: Generate ETL Notebooks
    run: python generate_notebooks.py
  
  - name: Deploy to Databricks
    run: databricks workspace import notebooks/
```

---

## FAQ

**Q: Can I generate notebooks for multiple targets from one source?**
A: Yes, include mappings for each target object. The generator will create separate transformation sections.

**Q: How do I handle complex joins?**
A: For simple scenarios, map from the same source. For complex joins, generate base notebook and add custom join logic.

**Q: Can I customize the generated code?**
A: Yes, the generated code is standard PySpark. Edit as needed after generation.

**Q: Does this support streaming?**
A: Currently batch-only. For streaming, use generated notebook as template and add streaming logic.

**Q: How do I handle CDC (Change Data Capture)?**
A: Generate base notebook with "merge" write mode, then enhance with Delta merge logic.

**Q: Can I use custom transformations?**
A: Yes, add custom UDFs to the notebook after generation or extend the transformation engine.

**Q: What about error handling?**
A: Notebooks include basic error handling. Add custom retry logic or error tables as needed.

**Q: How do I monitor execution?**
A: Use Databricks job monitoring, or add custom logging to Azure Log Analytics/Cloudwatch.

---

## Support and Resources

### Documentation
- [Databricks PySpark Guide](https://docs.databricks.com/spark/latest/spark-sql/language-manual/index.html)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Spark Performance Tuning](https://spark.apache.org/docs/latest/tuning.html)

### Sample Mappings
See `examples/` directory for:
- Simple CSV to Delta
- JDBC to Delta with transformations
- Multi-source aggregations
- SCD Type 2 patterns

---

## Changelog

### Version 0.1.0 (Initial Release)
- ETL notebook generation from mappings
- Support for CSV, Parquet, Delta, JSON, JDBC sources
- Support for Delta, Parquet, CSV, JDBC targets
- 15+ built-in transformations
- Data quality validation
- Direct workspace deployment
- Three optimization levels
- Comprehensive documentation

---

## License

Part of the AIDA project. See main license file.

---

## Quick Reference

### Minimum Required Mapping
```python
{
    "mapping_name": "Field1",
    "source_type": "CSV",
    "target_type": "Delta",
    "source_object": "source.csv",
    "source_field": "col1",
    "target_object": "target_table",
    "target_field": "col1"
}
```

### Generate & Deploy
```python
result = DatabricksETLNotebookGenerator(
    mappings=[...],
    notebook_name="My_ETL",
    notebook_path="/Users/me/ETL/My_ETL",
    deploy_to_workspace=True
)
```

### Common Transformations
- String: `TRIM, UPPER, LOWER, INITCAP`
- Type: `CAST AS STRING/INTEGER/DOUBLE/DATE`
- Security: `SHA256, MD5`
- Text: `REPLACE('old','new'), SUBSTRING(1,10)`

---

**Ready to generate your first ETL notebook? Start with a simple mapping and scale up!** 🚀
