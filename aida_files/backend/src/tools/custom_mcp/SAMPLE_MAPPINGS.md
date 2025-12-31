# Sample ETL Mappings for Testing

## Example 1: Customer Dimension (Simple)

```python
customer_mappings = [
    {
        "mapping_name": "Customer_ID",
        "mapping_complexity": "Simple",
        "source_name": "CRM_System",
        "target_name": "Analytics_DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "crm_customers.csv",
        "source_field": "customer_id",
        "transformation_logic": "CAST AS STRING, TRIM",
        "target_object": "dim_customer",
        "target_field": "customer_key"
    },
    {
        "mapping_name": "Customer_FirstName",
        "mapping_complexity": "Simple",
        "source_name": "CRM_System",
        "target_name": "Analytics_DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "crm_customers.csv",
        "source_field": "first_name",
        "transformation_logic": "TRIM, INITCAP",
        "target_object": "dim_customer",
        "target_field": "first_name"
    },
    {
        "mapping_name": "Customer_LastName",
        "mapping_complexity": "Simple",
        "source_name": "CRM_System",
        "target_name": "Analytics_DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "crm_customers.csv",
        "source_field": "last_name",
        "transformation_logic": "TRIM, INITCAP",
        "target_object": "dim_customer",
        "target_field": "last_name"
    },
    {
        "mapping_name": "Customer_Email",
        "mapping_complexity": "Medium",
        "source_name": "CRM_System",
        "target_name": "Analytics_DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "crm_customers.csv",
        "source_field": "email_address",
        "transformation_logic": "TRIM, LOWER",
        "target_object": "dim_customer",
        "target_field": "email"
    },
    {
        "mapping_name": "Customer_Phone",
        "mapping_complexity": "Medium",
        "source_name": "CRM_System",
        "target_name": "Analytics_DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "crm_customers.csv",
        "source_field": "phone_number",
        "transformation_logic": "REPLACE('-',''), REPLACE(' ','')",
        "target_object": "dim_customer",
        "target_field": "phone"
    }
]
```

## Example 2: Orders Fact Table (JDBC to Delta)

```python
orders_mappings = [
    {
        "mapping_name": "Order_ID",
        "mapping_complexity": "Simple",
        "source_name": "ERP_Database",
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
        "mapping_name": "Customer_ID",
        "mapping_complexity": "Simple",
        "source_name": "ERP_Database",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "customer_id",
        "transformation_logic": "CAST AS STRING, TRIM",
        "target_object": "fact_orders",
        "target_field": "customer_key"
    },
    {
        "mapping_name": "Order_Date",
        "mapping_complexity": "Simple",
        "source_name": "ERP_Database",
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
        "mapping_name": "Order_Amount",
        "mapping_complexity": "Medium",
        "source_name": "ERP_Database",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "total_amount",
        "transformation_logic": "CAST AS DOUBLE, COALESCE_NULL",
        "target_object": "fact_orders",
        "target_field": "order_amount"
    },
    {
        "mapping_name": "Order_Status",
        "mapping_complexity": "Simple",
        "source_name": "ERP_Database",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "status",
        "transformation_logic": "TRIM, UPPER",
        "target_object": "fact_orders",
        "target_field": "order_status"
    },
    {
        "mapping_name": "Product_ID",
        "mapping_complexity": "Simple",
        "source_name": "ERP_Database",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "product_id",
        "transformation_logic": "CAST AS STRING",
        "target_object": "fact_orders",
        "target_field": "product_key"
    },
    {
        "mapping_name": "Quantity",
        "mapping_complexity": "Simple",
        "source_name": "ERP_Database",
        "target_name": "Data_Lake",
        "source_type": "JDBC",
        "target_type": "Delta",
        "source_object": "orders",
        "source_field": "quantity",
        "transformation_logic": "CAST AS INTEGER",
        "target_object": "fact_orders",
        "target_field": "order_quantity"
    }
]
```

## Example 3: Employee Data with Masking (Complex)

```python
employee_mappings = [
    {
        "mapping_name": "Employee_ID",
        "mapping_complexity": "Simple",
        "source_name": "HR_System",
        "target_name": "Analytics",
        "source_type": "Parquet",
        "target_type": "Delta",
        "source_object": "employees.parquet",
        "source_field": "emp_id",
        "transformation_logic": "CAST AS STRING, TRIM",
        "target_object": "dim_employee",
        "target_field": "employee_key"
    },
    {
        "mapping_name": "Employee_Name",
        "mapping_complexity": "Medium",
        "source_name": "HR_System",
        "target_name": "Analytics",
        "source_type": "Parquet",
        "target_type": "Delta",
        "source_object": "employees.parquet",
        "source_field": "full_name",
        "transformation_logic": "TRIM, INITCAP",
        "target_object": "dim_employee",
        "target_field": "employee_name"
    },
    {
        "mapping_name": "SSN_Masked",
        "mapping_complexity": "Complex",
        "source_name": "HR_System",
        "target_name": "Analytics",
        "source_type": "Parquet",
        "target_type": "Delta",
        "source_object": "employees.parquet",
        "source_field": "ssn",
        "transformation_logic": "SHA256",
        "target_object": "dim_employee",
        "target_field": "ssn_hash"
    },
    {
        "mapping_name": "Salary",
        "mapping_complexity": "Medium",
        "source_name": "HR_System",
        "target_name": "Analytics",
        "source_type": "Parquet",
        "target_type": "Delta",
        "source_object": "employees.parquet",
        "source_field": "annual_salary",
        "transformation_logic": "CAST AS DOUBLE",
        "target_object": "dim_employee",
        "target_field": "salary_amount"
    },
    {
        "mapping_name": "Hire_Date",
        "mapping_complexity": "Simple",
        "source_name": "HR_System",
        "target_name": "Analytics",
        "source_type": "Parquet",
        "target_type": "Delta",
        "source_object": "employees.parquet",
        "source_field": "hire_date",
        "transformation_logic": "CAST AS DATE",
        "target_object": "dim_employee",
        "target_field": "hire_date"
    },
    {
        "mapping_name": "Department",
        "mapping_complexity": "Simple",
        "source_name": "HR_System",
        "target_name": "Analytics",
        "source_type": "Parquet",
        "target_type": "Delta",
        "source_object": "employees.parquet",
        "source_field": "dept_name",
        "transformation_logic": "TRIM, UPPER",
        "target_object": "dim_employee",
        "target_field": "department"
    }
]
```

## Example 4: Sales Transactions (JSON to Delta)

```python
sales_mappings = [
    {
        "mapping_name": "Transaction_ID",
        "mapping_complexity": "Simple",
        "source_name": "POS_System",
        "target_name": "Sales_DW",
        "source_type": "JSON",
        "target_type": "Delta",
        "source_object": "transactions.json",
        "source_field": "transaction_id",
        "transformation_logic": "CAST AS STRING",
        "target_object": "fact_sales",
        "target_field": "transaction_key"
    },
    {
        "mapping_name": "Store_ID",
        "mapping_complexity": "Simple",
        "source_name": "POS_System",
        "target_name": "Sales_DW",
        "source_type": "JSON",
        "target_type": "Delta",
        "source_object": "transactions.json",
        "source_field": "store_id",
        "transformation_logic": "CAST AS STRING, TRIM, UPPER",
        "target_object": "fact_sales",
        "target_field": "store_key"
    },
    {
        "mapping_name": "Sale_Amount",
        "mapping_complexity": "Medium",
        "source_name": "POS_System",
        "target_name": "Sales_DW",
        "source_type": "JSON",
        "target_type": "Delta",
        "source_object": "transactions.json",
        "source_field": "total_amount",
        "transformation_logic": "CAST AS DOUBLE, COALESCE_NULL",
        "target_object": "fact_sales",
        "target_field": "sale_amount"
    },
    {
        "mapping_name": "Transaction_Timestamp",
        "mapping_complexity": "Medium",
        "source_name": "POS_System",
        "target_name": "Sales_DW",
        "source_type": "JSON",
        "target_type": "Delta",
        "source_object": "transactions.json",
        "source_field": "timestamp",
        "transformation_logic": "CAST AS TIMESTAMP",
        "target_object": "fact_sales",
        "target_field": "sale_timestamp"
    },
    {
        "mapping_name": "Payment_Method",
        "mapping_complexity": "Simple",
        "source_name": "POS_System",
        "target_name": "Sales_DW",
        "source_type": "JSON",
        "target_type": "Delta",
        "source_object": "transactions.json",
        "source_field": "payment_type",
        "transformation_logic": "TRIM, UPPER",
        "target_object": "fact_sales",
        "target_field": "payment_method"
    }
]
```

## Example 5: Product Dimension (Delta to Delta)

```python
product_mappings = [
    {
        "mapping_name": "Product_ID",
        "mapping_complexity": "Simple",
        "source_name": "Product_Master",
        "target_name": "Analytics_DW",
        "source_type": "Delta",
        "target_type": "Delta",
        "source_object": "bronze_products",
        "source_field": "product_id",
        "transformation_logic": "CAST AS STRING, TRIM",
        "target_object": "dim_product",
        "target_field": "product_key"
    },
    {
        "mapping_name": "Product_Name",
        "mapping_complexity": "Medium",
        "source_name": "Product_Master",
        "target_name": "Analytics_DW",
        "source_type": "Delta",
        "target_type": "Delta",
        "source_object": "bronze_products",
        "source_field": "product_name",
        "transformation_logic": "TRIM, INITCAP",
        "target_object": "dim_product",
        "target_field": "product_name"
    },
    {
        "mapping_name": "Product_SKU",
        "mapping_complexity": "Medium",
        "source_name": "Product_Master",
        "target_name": "Analytics_DW",
        "source_type": "Delta",
        "target_type": "Delta",
        "source_object": "bronze_products",
        "source_field": "sku",
        "transformation_logic": "TRIM, UPPER, REPLACE('-','')",
        "target_object": "dim_product",
        "target_field": "sku_code"
    },
    {
        "mapping_name": "Product_Category",
        "mapping_complexity": "Simple",
        "source_name": "Product_Master",
        "target_name": "Analytics_DW",
        "source_type": "Delta",
        "target_type": "Delta",
        "source_object": "bronze_products",
        "source_field": "category",
        "transformation_logic": "TRIM, UPPER",
        "target_object": "dim_product",
        "target_field": "category_name"
    },
    {
        "mapping_name": "Unit_Price",
        "mapping_complexity": "Simple",
        "source_name": "Product_Master",
        "target_name": "Analytics_DW",
        "source_type": "Delta",
        "target_type": "Delta",
        "source_object": "bronze_products",
        "source_field": "unit_price",
        "transformation_logic": "CAST AS DOUBLE",
        "target_object": "dim_product",
        "target_field": "unit_price"
    },
    {
        "mapping_name": "Product_Description",
        "mapping_complexity": "Simple",
        "source_name": "Product_Master",
        "target_name": "Analytics_DW",
        "source_type": "Delta",
        "target_type": "Delta",
        "source_object": "bronze_products",
        "source_field": "description",
        "transformation_logic": "TRIM",
        "target_object": "dim_product",
        "target_field": "product_description"
    }
]
```

## How to Use These Samples

### Option 1: Copy and Execute

```python
from Databricks_ETL_Generator_mcp import DatabricksETLNotebookGenerator

# Use one of the sample mappings above
result = DatabricksETLNotebookGenerator(
    mappings=customer_mappings,  # or orders_mappings, employee_mappings, etc.
    notebook_name="Customer_ETL_v1",
    optimization_level="standard"
)

# Print the generated code
print(result["data"]["notebook_code"])

# Or save to file
with open("Customer_ETL.py", "w") as f:
    f.write(result["data"]["notebook_code"])
```

### Option 2: Deploy to Workspace

```python
result = DatabricksETLNotebookGenerator(
    mappings=orders_mappings,
    notebook_name="Orders_ETL_Pipeline",
    notebook_path="/Users/your.email@company.com/ETL/Orders",
    deploy_to_workspace=True,
    optimization_level="advanced"
)

if result["success"] and result.get("deployment"):
    print(f"Deployed to: {result['deployment']['notebook_url']}")
```

### Option 3: Use with AI Assistant

Simply tell your AI assistant:

"Generate a Databricks ETL notebook using the customer_mappings from the sample file"

Or:

"Create an ETL notebook for orders data with these fields:
- order_id → order_key (cast to string)
- customer_id → customer_key (trim and cast)
- order_date → order_date (cast to date)
- total_amount → order_amount (cast to double)
Source is JDBC from orders table, target is Delta to fact_orders"

## Mapping Templates for Excel/CSV

If your client provides mappings in Excel, convert using this template:

### CSV Format
```csv
Mapping Name,Mapping Complexity,Source Name,Target Name,Source Type,Target Type,Source Object,Source Field,Transformation Logic,Target Object,Target Field
Customer_ID,Simple,CRM,DW,CSV,Delta,customers.csv,customer_id,"CAST AS STRING, TRIM",dim_customer,customer_key
Customer_Name,Simple,CRM,DW,CSV,Delta,customers.csv,full_name,"TRIM, INITCAP",dim_customer,customer_name
```

### Python Conversion Function
```python
import csv

def csv_to_mappings(csv_file):
    mappings = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mappings.append({
                "mapping_name": row["Mapping Name"],
                "mapping_complexity": row["Mapping Complexity"],
                "source_name": row["Source Name"],
                "target_name": row["Target Name"],
                "source_type": row["Source Type"],
                "target_type": row["Target Type"],
                "source_object": row["Source Object"],
                "source_field": row["Source Field"],
                "transformation_logic": row["Transformation Logic"],
                "target_object": row["Target Object"],
                "target_field": row["Target Field"]
            })
    return mappings

# Usage
mappings = csv_to_mappings("client_mappings.csv")
result = DatabricksETLNotebookGenerator(mappings=mappings, notebook_name="Client_ETL")
```

## Testing Individual Mappings

Test with a single mapping first:

```python
test_mapping = [{
    "mapping_name": "Test_Field",
    "mapping_complexity": "Simple",
    "source_name": "Test_Source",
    "target_name": "Test_Target",
    "source_type": "CSV",
    "target_type": "Delta",
    "source_object": "test.csv",
    "source_field": "test_col",
    "transformation_logic": "TRIM, UPPER",
    "target_object": "test_table",
    "target_field": "test_field"
}]

result = DatabricksETLNotebookGenerator(
    mappings=test_mapping,
    notebook_name="Test_ETL"
)

# Verify notebook was generated
assert result["success"]
assert "test_col" in result["data"]["notebook_code"]
assert "test_field" in result["data"]["notebook_code"]
```

## Need More Examples?

Contact your data engineering team or refer to:
- [Full Generator Guide](./DATABRICKS_ETL_GENERATOR_GUIDE.md)
- [Databricks MCP Guide](./DATABRICKS_MCP_GUIDE.md)
- [Quick Reference](./DATABRICKS_QUICK_REF.md)
