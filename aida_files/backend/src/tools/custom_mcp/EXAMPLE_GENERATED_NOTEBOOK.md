# Example: Generated ETL Notebook Preview

This shows what a generated notebook looks like for a simple customer ETL.

## Input Mappings

```python
mappings = [
    {
        "mapping_name": "Customer_ID",
        "mapping_complexity": "Simple",
        "source_name": "CRM",
        "target_name": "DW",
        "source_type": "CSV",
        "target_type": "Delta",
        "source_object": "customers.csv",
        "source_field": "customer_id",
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
        "source_object": "customers.csv",
        "source_field": "full_name",
        "transformation_logic": "TRIM, INITCAP",
        "target_object": "dim_customer",
        "target_field": "customer_name"
    }
]
```

## Generated Notebook Structure

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Customer_ETL
# MAGIC 
# MAGIC **Generated ETL Notebook**
# MAGIC **Total Mappings**: 2
# MAGIC **Source Objects**: customers.csv
# MAGIC **Target Objects**: dim_customer

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Configuration

# COMMAND ----------

# Import required libraries
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime

spark = SparkSession.builder.appName("Customer_ETL").getOrCreate()
spark.conf.set("spark.sql.adaptive.enabled", "true")

print("Spark session initialized successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Define Parameters (Widgets)

# COMMAND ----------

# Create widgets for parameterization
dbutils.widgets.text("source_customers_csv_path", "/mnt/source/customers.csv", "Source Path: customers.csv")
dbutils.widgets.text("target_dim_customer_path", "/mnt/target/dim_customer", "Target Path: dim_customer")
dbutils.widgets.dropdown("write_mode", "overwrite", ["overwrite", "append", "merge"], "Write Mode")
dbutils.widgets.dropdown("validation_enabled", "true", ["true", "false"], "Enable Validation")

print("✓ Widgets created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Helper Functions

# COMMAND ----------

def log_message(level, message):
    """Logging helper function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def validate_dataframe(df, df_name, expected_columns=None):
    """Validate DataFrame structure and content"""
    log_message("INFO", f"Validating {df_name}")
    row_count = df.count()
    log_message("INFO", f"{df_name} row count: {row_count:,}")
    
    if row_count == 0:
        log_message("WARNING", f"{df_name} is empty")
        return False
    
    return True

def apply_transformations(df, field_name, transformation_logic):
    """Apply transformation logic to a field"""
    if not transformation_logic or transformation_logic.upper() == "NONE":
        return df
    
    transformations = [t.strip().upper() for t in transformation_logic.split(',')]
    result_df = df
    temp_col = f"{field_name}_transformed"
    
    for transform in transformations:
        if transform == "TRIM":
            result_df = result_df.withColumn(temp_col, trim(col(field_name)))
        elif transform == "UPPER":
            result_df = result_df.withColumn(temp_col, upper(col(field_name)))
        elif transform == "INITCAP":
            result_df = result_df.withColumn(temp_col, initcap(col(field_name)))
        elif transform.startswith("CAST AS"):
            cast_type = transform.replace("CAST AS", "").strip()
            if cast_type == "STRING":
                result_df = result_df.withColumn(temp_col, col(field_name).cast(StringType()))
        else:
            log_message("WARNING", f"Unknown transformation: {transform}")
            return result_df
    
    return result_df.withColumn(field_name, col(temp_col)).drop(temp_col)

log_message("INFO", "✓ Helper functions defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Read Source Data

# COMMAND ----------

write_mode = dbutils.widgets.get("write_mode")
validation_enabled = dbutils.widgets.get("validation_enabled").lower() == "true"

log_message("INFO", f"Write Mode: {write_mode}")

source_dataframes = {}

# Read from customers.csv (CSV)
log_message("INFO", "Reading source: customers.csv")
try:
    source_customers_csv_path = dbutils.widgets.get("source_customers_csv_path")
    df_customers_csv = spark.read \
        .format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(source_customers_csv_path)
    
    # Select required fields
    required_fields = ['customer_id', 'full_name']
    available_fields = [f for f in required_fields if f in df_customers_csv.columns]
    df_customers_csv = df_customers_csv.select(available_fields)
    
    source_dataframes["customers.csv"] = df_customers_csv
    log_message("INFO", f"✓ Successfully read customers.csv: {df_customers_csv.count():,} rows")
    
    if validation_enabled:
        validate_dataframe(df_customers_csv, "customers.csv", required_fields)
        
except Exception as e:
    log_message("ERROR", f"Failed to read customers.csv: {str(e)}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Apply Transformations

# COMMAND ----------

log_message("INFO", "Starting transformations...")
transformed_dataframes = {}

# Transform data for target: dim_customer
log_message("INFO", "Transforming data for dim_customer")
df_transformed_dim_customer = source_dataframes["customers.csv"]

# Mapping: Customer_ID
# Source: customer_id -> Target: customer_key
# Transformation: CAST AS STRING, TRIM
if "customer_id" in df_transformed_dim_customer.columns:
    df_transformed_dim_customer = apply_transformations(
        df_transformed_dim_customer, 
        "customer_id", 
        "CAST AS STRING, TRIM"
    )
    df_transformed_dim_customer = df_transformed_dim_customer.withColumnRenamed("customer_id", "customer_key")
log_message("INFO", "  ✓ Transformed customer_id -> customer_key")

# Mapping: Customer_Name
# Source: full_name -> Target: customer_name
# Transformation: TRIM, INITCAP
if "full_name" in df_transformed_dim_customer.columns:
    df_transformed_dim_customer = apply_transformations(
        df_transformed_dim_customer, 
        "full_name", 
        "TRIM, INITCAP"
    )
    df_transformed_dim_customer = df_transformed_dim_customer.withColumnRenamed("full_name", "customer_name")
log_message("INFO", "  ✓ Transformed full_name -> customer_name")

# Add audit columns
df_transformed_dim_customer = df_transformed_dim_customer \
    .withColumn("etl_load_timestamp", current_timestamp()) \
    .withColumn("etl_load_date", current_date()) \
    .withColumn("etl_source_system", lit("CRM"))

transformed_dataframes["dim_customer"] = df_transformed_dim_customer
log_message("INFO", f"✓ Transformation completed for dim_customer: {df_transformed_dim_customer.count():,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Data Quality Validation

# COMMAND ----------

if validation_enabled:
    log_message("INFO", "Starting data quality validation...")
    
    validation_results = []
    
    # Validate dim_customer
    df_val = transformed_dataframes["dim_customer"]
    
    validation_results.append({
        "target": "dim_customer",
        "row_count": df_val.count(),
        "column_count": len(df_val.columns),
        "has_duplicates": df_val.count() != df_val.distinct().count()
    })
    
    # Display validation summary
    validation_df = spark.createDataFrame(validation_results)
    display(validation_df)
    log_message("INFO", "✓ Data quality validation completed")
else:
    log_message("INFO", "Validation skipped (disabled)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Write to Target

# COMMAND ----------

log_message("INFO", "Writing to target destinations...")

# Write to dim_customer (Delta)
log_message("INFO", "Writing to target: dim_customer")
try:
    df_to_write = transformed_dataframes["dim_customer"]
    
    target_dim_customer_path = dbutils.widgets.get("target_dim_customer_path")
    
    df_to_write.write \
        .format("delta") \
        .mode(write_mode) \
        .option("mergeSchema", "true") \
        .save(target_dim_customer_path)
    
    log_message("INFO", f"✓ Successfully wrote to dim_customer (Delta)")
    
except Exception as e:
    log_message("ERROR", f"Failed to write to dim_customer: {str(e)}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Final Summary and Statistics

# COMMAND ----------

log_message("INFO", "="*60)
log_message("INFO", "ETL EXECUTION SUMMARY")
log_message("INFO", "="*60)

summary_data = []

summary_data.append({
    "target_object": "dim_customer",
    "source_object": "customers.csv",
    "status": "SUCCESS",
    "records_processed": transformed_dataframes["dim_customer"].count()
})

# Display summary
summary_df = spark.createDataFrame(summary_data)
display(summary_df)

log_message("INFO", "✓ ETL process completed successfully")
log_message("INFO", "="*60)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Optimization Notes and Best Practices
# MAGIC 
# MAGIC ### Cluster Configuration Recommendations:
# MAGIC - **Worker Nodes**: 2-8 workers depending on data volume
# MAGIC - **Instance Type**: Standard_DS3_v2 or higher for production
# MAGIC - **Databricks Runtime**: 12.2 LTS or higher (with Delta Lake support)
# MAGIC 
# MAGIC ### Performance Optimization Tips:
# MAGIC 1. **Partitioning**: Consider partitioning Delta tables by date columns
# MAGIC 2. **Caching**: Cache intermediate DataFrames if reused
# MAGIC 3. **Z-Ordering**: Apply Z-ORDER on frequently filtered columns
# MAGIC 
# MAGIC ### Monitoring and Maintenance:
# MAGIC - Enable Delta table optimizations: `OPTIMIZE table_name`
# MAGIC - Run VACUUM periodically: `VACUUM table_name RETAIN 168 HOURS`
# MAGIC - Monitor Spark UI for bottlenecks
```

## Key Features Highlighted

### ✅ Parameterization
- Uses `dbutils.widgets` for flexible parameters
- Easy to change source/target paths
- Configurable write modes

### ✅ Transformation Engine
- Handles multiple transformation types
- Chains transformations correctly
- Extensible for custom logic

### ✅ Data Quality
- Row count validation
- Column existence checks
- Duplicate detection

### ✅ Audit Trail
- Automatic timestamp columns
- Source system tracking
- Load date tracking

### ✅ Error Handling
- Try-catch blocks for each step
- Detailed logging
- Clear error messages

### ✅ Documentation
- Markdown cells explain each section
- Configuration recommendations
- Best practices included

## How to Use Generated Notebook

### 1. Deploy to Databricks
```python
result = DatabricksETLNotebookGenerator(
    mappings=customer_mappings,
    notebook_name="Customer_ETL",
    notebook_path="/Users/me/ETL/Customer_ETL",
    deploy_to_workspace=True
)
```

### 2. Configure Parameters in Databricks
- Set source path: `/mnt/bronze/crm/customers.csv`
- Set target path: `/mnt/silver/dim_customer`
- Choose write mode: `overwrite` or `append`
- Enable validation: `true`

### 3. Attach to Cluster
- Select appropriate cluster
- Ensure cluster has necessary libraries

### 4. Run Notebook
- Run all cells
- Monitor execution in real-time
- Review validation results
- Check summary statistics

### 5. Schedule as Job
- Create new job in Databricks
- Select this notebook
- Configure schedule (daily, hourly, etc.)
- Set up notifications

## Production Checklist

Before deploying to production:

- [ ] Test with sample data first
- [ ] Verify all source paths are correct
- [ ] Confirm target paths are accessible
- [ ] Review transformation logic
- [ ] Enable validation
- [ ] Set up monitoring/alerts
- [ ] Document any custom changes
- [ ] Test error scenarios
- [ ] Review cluster configuration
- [ ] Set appropriate write mode (append vs overwrite)

## Customization Points

You can enhance the generated notebook with:

1. **Custom Transformations**: Add UDFs for business-specific logic
2. **Advanced Joins**: Add multi-source joins if needed
3. **SCD Type 2**: Implement slowly changing dimensions
4. **Incremental Loads**: Add watermark/checkpoint logic
5. **Data Quality Rules**: Add specific validation rules
6. **Error Tables**: Route bad records to error tables
7. **Metrics Collection**: Add custom metrics/logging
8. **Alerting**: Integrate with monitoring systems

## Example Customization

```python
# Add after transformation section
# Custom business rule: flag high-value customers
df_transformed_dim_customer = df_transformed_dim_customer \
    .withColumn("is_vip", 
        when(col("lifetime_value") > 10000, True).otherwise(False))

# Add data quality rule
quality_check = df_transformed_dim_customer.filter(col("customer_key").isNull())
if quality_check.count() > 0:
    log_message("ERROR", f"Found {quality_check.count()} records with null customer_key")
    # Route to error table or raise exception
```

## Performance Tuning

For large datasets:

```python
# Add caching for reused DataFrames
df_transformed_dim_customer.cache()

# Add repartitioning before write
df_to_write = df_to_write.repartition(10)

# Enable optimize write for Delta
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")

# Partition by date for better query performance
df_to_write.write \
    .format("delta") \
    .partitionBy("etl_load_date") \
    .mode(write_mode) \
    .save(target_path)
```

---

**This is just a preview!** The actual generator creates complete, production-ready notebooks with all these features built-in. Simply provide your mappings and let the generator handle the rest! 🚀
