import os
import json
import base64
import urllib3
from typing import Dict, List, Optional
from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv(find_dotenv(), verbose=True, override=True)

# SSL Configuration - disable warnings if SSL verification is skipped
SKIP_SSL_VERIFY = os.getenv('DATABRICKS_SKIP_SSL_VERIFY', 'false').lower() == 'true'
if SKIP_SSL_VERIFY:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


mcp = FastMCP("Databricks ETL MCP Server", "0.1.0")


@mcp.tool()
def DatabricksETLNotebookGenerator(
    mappings: List[Dict],
    notebook_name: str = "ETL_Notebook",
    notebook_path: str = None,
    deploy_to_workspace: bool = False,
    optimization_level: str = "standard"
) -> dict:
    """
    Generate Databricks PySpark ETL Notebook from Mapping Specifications.
    
    Creates a parameterized, production-ready Databricks notebook based on client-provided
    ETL mappings. The notebook includes widgets, transformation logic, validation, and
    optimization hints.
    
    Args:
        mappings (List[Dict]): List of mapping dictionaries with fields:
            - mapping_name: Name/identifier for this mapping
            - mapping_complexity: Simple/Medium/Complex
            - source_name: Logical source name
            - target_name: Logical target name
            - source_type: CSV/Parquet/Delta/JDBC/JSON
            - target_type: Delta/Parquet/CSV/JDBC
            - source_object: Table name or file path
            - source_field: Source column name
            - transformation_logic: Transformation to apply
            - target_object: Target table name or path
            - target_field: Target column name
            
        notebook_name (str): Name for the generated notebook
        notebook_path (str): Workspace path to deploy notebook (e.g., /Users/user@example.com/ETL)
        deploy_to_workspace (bool): If True, deploy directly to Databricks workspace
        optimization_level (str): standard/advanced/maximum - level of optimization to include
        
    Returns:
        dict: Contains generated notebook code, metadata, and deployment status
        
    Example:
        mappings = [
            {
                "mapping_name": "Customer_Transform",
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
            },
            {
                "mapping_name": "Customer_Name",
                "mapping_complexity": "Simple",
                "source_name": "CRM_DB",
                "target_name": "Analytics_DW",
                "source_type": "JDBC",
                "target_type": "Delta",
                "source_object": "customers",
                "source_field": "full_name",
                "transformation_logic": "TRIM, INITCAP",
                "target_object": "dim_customer",
                "target_field": "customer_name"
            }
        ]
        
        result = DatabricksETLNotebookGenerator(
            mappings=mappings,
            notebook_name="Customer_ETL_v1",
            notebook_path="/Users/user@example.com/ETL/Customer_ETL_v1",
            deploy_to_workspace=True
        )
    """
    
    try:
        # Validate mappings
        if not mappings or not isinstance(mappings, list):
            return {
                "success": False,
                "error": "Invalid mappings",
                "message": "Mappings must be a non-empty list of dictionaries"
            }
        
        # Required mapping fields
        required_fields = [
            "mapping_name", "source_type", "target_type", 
            "source_object", "source_field", "target_object", "target_field"
        ]
        
        for idx, mapping in enumerate(mappings):
            missing = [f for f in required_fields if f not in mapping]
            if missing:
                return {
                    "success": False,
                    "error": f"Missing required fields in mapping {idx}",
                    "message": f"Required fields: {', '.join(missing)}"
                }
        
        # Group mappings by source and target
        source_objects = {}
        target_objects = {}
        
        for mapping in mappings:
            src_obj = mapping["source_object"]
            tgt_obj = mapping["target_object"]
            
            if src_obj not in source_objects:
                source_objects[src_obj] = {
                    "type": mapping["source_type"],
                    "fields": [],
                    "mappings": []
                }
            source_objects[src_obj]["fields"].append(mapping["source_field"])
            source_objects[src_obj]["mappings"].append(mapping)
            
            if tgt_obj not in target_objects:
                target_objects[tgt_obj] = {
                    "type": mapping["target_type"],
                    "fields": [],
                    "mappings": []
                }
            target_objects[tgt_obj]["fields"].append(mapping["target_field"])
            target_objects[tgt_obj]["mappings"].append(mapping)
        
        # Generate notebook code
        notebook_code = _generate_etl_notebook(
            mappings, 
            source_objects, 
            target_objects, 
            notebook_name,
            optimization_level
        )
        
        result = {
            "success": True,
            "data": {
                "notebook_name": notebook_name,
                "notebook_code": notebook_code,
                "total_mappings": len(mappings),
                "source_objects": list(source_objects.keys()),
                "target_objects": list(target_objects.keys()),
                "complexity_distribution": _get_complexity_stats(mappings)
            },
            "message": f"Successfully generated ETL notebook with {len(mappings)} mappings"
        }
        
        # Deploy to workspace if requested
        if deploy_to_workspace and notebook_path:
            deploy_result = _deploy_notebook_to_workspace(notebook_path, notebook_code)
            result["deployment"] = deploy_result
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate ETL notebook"
        }


def _generate_etl_notebook(mappings, source_objects, target_objects, notebook_name, optimization_level):
    """Generate the complete PySpark notebook code"""
    
    # Get unique source and target types
    source_types = set(m["source_type"] for m in mappings)
    target_types = set(m["target_type"] for m in mappings)
    
    code = f'''# Databricks notebook source
# MAGIC %md
# MAGIC # {notebook_name}
# MAGIC 
# MAGIC **Generated ETL Notebook**
# MAGIC 
# MAGIC **Purpose**: Automated data transformation based on mapping specifications
# MAGIC 
# MAGIC **Total Mappings**: {len(mappings)}
# MAGIC 
# MAGIC **Source Objects**: {", ".join(source_objects.keys())}
# MAGIC 
# MAGIC **Target Objects**: {", ".join(target_objects.keys())}
# MAGIC 
# MAGIC **Generated On**: Auto-generated by Databricks ETL MCP

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Configuration

# COMMAND ----------

# Import required libraries
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
from datetime import datetime
import hashlib

# Initialize Spark session
spark = SparkSession.builder.appName("{notebook_name}").getOrCreate()

# Set configurations for optimization
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
'''

    if optimization_level in ["advanced", "maximum"]:
        code += '''spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
'''

    code += '''
print("Spark session initialized successfully")
print(f"Spark version: {{spark.version}}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Define Parameters (Widgets)

# COMMAND ----------

# Create widgets for parameterization
'''

    # Add widgets for each unique source and target
    for src_obj in source_objects.keys():
        src_type = source_objects[src_obj]["type"]
        if src_type in ["CSV", "Parquet", "Delta", "JSON"]:
            code += f'''dbutils.widgets.text("source_{_sanitize_name(src_obj)}_path", "/mnt/source/{src_obj}", "Source Path: {src_obj}")
'''
        elif src_type == "JDBC":
            code += f'''dbutils.widgets.text("source_{_sanitize_name(src_obj)}_jdbc_url", "jdbc:sqlserver://server:1433;database=db", "JDBC URL: {src_obj}")
dbutils.widgets.text("source_{_sanitize_name(src_obj)}_table", "{src_obj}", "Source Table: {src_obj}")
'''

    for tgt_obj in target_objects.keys():
        tgt_type = target_objects[tgt_obj]["type"]
        if tgt_type in ["Delta", "Parquet", "CSV"]:
            code += f'''dbutils.widgets.text("target_{_sanitize_name(tgt_obj)}_path", "/mnt/target/{tgt_obj}", "Target Path: {tgt_obj}")
'''
        elif tgt_type == "JDBC":
            code += f'''dbutils.widgets.text("target_{_sanitize_name(tgt_obj)}_jdbc_url", "jdbc:sqlserver://server:1433;database=db", "Target JDBC URL: {tgt_obj}")
dbutils.widgets.text("target_{_sanitize_name(tgt_obj)}_table", "{tgt_obj}", "Target Table: {tgt_obj}")
'''

    code += '''dbutils.widgets.dropdown("write_mode", "overwrite", ["overwrite", "append", "merge"], "Write Mode")
dbutils.widgets.dropdown("validation_enabled", "true", ["true", "false"], "Enable Validation")
dbutils.widgets.text("secret_scope", "databricks-secrets", "Secret Scope Name")

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
    
    # Check if DataFrame is empty
    row_count = df.count()
    log_message("INFO", f"{df_name} row count: {row_count:,}")
    
    if row_count == 0:
        log_message("WARNING", f"{df_name} is empty")
        return False
    
    # Check schema
    log_message("INFO", f"{df_name} columns: {', '.join(df.columns)}")
    
    # Check for expected columns
    if expected_columns:
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            log_message("ERROR", f"{df_name} missing columns: {missing_cols}")
            return False
    
    # Check for nulls in key columns
    null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).collect()[0].asDict()
    for col_name, null_count in null_counts.items():
        if null_count > 0:
            log_message("WARNING", f"{df_name}.{col_name} has {null_count:,} null values")
    
    log_message("INFO", f"✓ {df_name} validation completed")
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
        elif transform == "LOWER":
            result_df = result_df.withColumn(temp_col, lower(col(field_name)))
        elif transform == "INITCAP":
            result_df = result_df.withColumn(temp_col, initcap(col(field_name)))
        elif transform.startswith("CAST AS"):
            cast_type = transform.replace("CAST AS", "").strip()
            if cast_type == "STRING":
                result_df = result_df.withColumn(temp_col, col(field_name).cast(StringType()))
            elif cast_type == "INT" or cast_type == "INTEGER":
                result_df = result_df.withColumn(temp_col, col(field_name).cast(IntegerType()))
            elif cast_type == "LONG" or cast_type == "BIGINT":
                result_df = result_df.withColumn(temp_col, col(field_name).cast(LongType()))
            elif cast_type == "DOUBLE" or cast_type == "FLOAT":
                result_df = result_df.withColumn(temp_col, col(field_name).cast(DoubleType()))
            elif cast_type == "DATE":
                result_df = result_df.withColumn(temp_col, col(field_name).cast(DateType()))
            elif cast_type == "TIMESTAMP":
                result_df = result_df.withColumn(temp_col, col(field_name).cast(TimestampType()))
        elif transform.startswith("SUBSTRING"):
            # Extract SUBSTRING(1,10) pattern
            import re
            match = re.search(r'SUBSTRING\\((\\d+),(\\d+)\\)', transform)
            if match:
                start, length = int(match.group(1)), int(match.group(2))
                result_df = result_df.withColumn(temp_col, substring(col(field_name), start, length))
        elif transform == "HASH" or transform == "MD5":
            result_df = result_df.withColumn(temp_col, md5(col(field_name)))
        elif transform == "SHA256":
            result_df = result_df.withColumn(temp_col, sha2(col(field_name), 256))
        elif transform.startswith("REPLACE"):
            # Extract REPLACE('old','new') pattern
            import re
            match = re.search(r"REPLACE\\('([^']*)','([^']*)'\\)", transform)
            if match:
                old_val, new_val = match.group(1), match.group(2)
                result_df = result_df.withColumn(temp_col, regexp_replace(col(field_name), old_val, new_val))
        elif transform == "COALESCE_NULL":
            result_df = result_df.withColumn(temp_col, coalesce(col(field_name), lit("")))
        else:
            log_message("WARNING", f"Unknown transformation: {transform}")
            return result_df
    
    return result_df.withColumn(field_name, col(temp_col)).drop(temp_col)

log_message("INFO", "✓ Helper functions defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Read Source Data

# COMMAND ----------

# Read parameters
write_mode = dbutils.widgets.get("write_mode")
validation_enabled = dbutils.widgets.get("validation_enabled").lower() == "true"
secret_scope = dbutils.widgets.get("secret_scope")

log_message("INFO", f"Write Mode: {write_mode}")
log_message("INFO", f"Validation Enabled: {validation_enabled}")

# Read source data
source_dataframes = {{}}

'''

    # Generate read logic for each source
    for src_obj, src_info in source_objects.items():
        src_type = src_info["type"]
        src_fields = list(set(src_info["fields"]))  # Remove duplicates
        sanitized_name = _sanitize_name(src_obj)
        
        code += f'''
# Read from {src_obj} ({src_type})
log_message("INFO", "Reading source: {src_obj}")
try:
'''
        
        if src_type == "CSV":
            code += f'''    source_{sanitized_name}_path = dbutils.widgets.get("source_{sanitized_name}_path")
    df_{sanitized_name} = spark.read \\
        .format("csv") \\
        .option("header", "true") \\
        .option("inferSchema", "true") \\
        .load(source_{sanitized_name}_path)
'''
        elif src_type == "Parquet":
            code += f'''    source_{sanitized_name}_path = dbutils.widgets.get("source_{sanitized_name}_path")
    df_{sanitized_name} = spark.read.parquet(source_{sanitized_name}_path)
'''
        elif src_type == "Delta":
            code += f'''    source_{sanitized_name}_path = dbutils.widgets.get("source_{sanitized_name}_path")
    df_{sanitized_name} = spark.read.format("delta").load(source_{sanitized_name}_path)
'''
        elif src_type == "JSON":
            code += f'''    source_{sanitized_name}_path = dbutils.widgets.get("source_{sanitized_name}_path")
    df_{sanitized_name} = spark.read.json(source_{sanitized_name}_path)
'''
        elif src_type == "JDBC":
            code += f'''    jdbc_url = dbutils.widgets.get("source_{sanitized_name}_jdbc_url")
    table_name = dbutils.widgets.get("source_{sanitized_name}_table")
    # Retrieve credentials from secret scope
    username = dbutils.secrets.get(scope=secret_scope, key="jdbc_username")
    password = dbutils.secrets.get(scope=secret_scope, key="jdbc_password")
    
    df_{sanitized_name} = spark.read \\
        .format("jdbc") \\
        .option("url", jdbc_url) \\
        .option("dbtable", table_name) \\
        .option("user", username) \\
        .option("password", password) \\
        .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \\
        .load()
'''
        
        code += f'''    
    # Select required fields
    required_fields = {src_fields}
    available_fields = [f for f in required_fields if f in df_{sanitized_name}.columns]
    df_{sanitized_name} = df_{sanitized_name}.select(available_fields)
    
    source_dataframes["{src_obj}"] = df_{sanitized_name}
    log_message("INFO", f"✓ Successfully read {src_obj}: {{df_{sanitized_name}.count():,}} rows")
    
    if validation_enabled:
        validate_dataframe(df_{sanitized_name}, "{src_obj}", {src_fields})
        
except Exception as e:
    log_message("ERROR", f"Failed to read {src_obj}: {{str(e)}}")
    raise

'''

    code += '''
# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Apply Transformations

# COMMAND ----------

log_message("INFO", "Starting transformations...")

# Dictionary to store transformed dataframes for each target
transformed_dataframes = {}

'''

    # Group mappings by target object for transformation
    for tgt_obj, tgt_info in target_objects.items():
        sanitized_tgt = _sanitize_name(tgt_obj)
        tgt_mappings = tgt_info["mappings"]
        
        # Get source object (assume all mappings for same target come from same source for simplicity)
        # In complex scenarios, this would need joins
        src_obj = tgt_mappings[0]["source_object"]
        sanitized_src = _sanitize_name(src_obj)
        
        code += f'''
# Transform data for target: {tgt_obj}
log_message("INFO", "Transforming data for {tgt_obj}")
df_transformed_{sanitized_tgt} = source_dataframes["{src_obj}"]

# Apply field-level transformations
'''
        
        for mapping in tgt_mappings:
            src_field = mapping["source_field"]
            tgt_field = mapping["target_field"]
            transform_logic = mapping.get("transformation_logic", "NONE")
            
            code += f'''
# Mapping: {mapping.get("mapping_name", "Unnamed")}
# Source: {src_field} -> Target: {tgt_field}
# Transformation: {transform_logic}
'''
            
            if src_field != tgt_field or transform_logic.upper() != "NONE":
                code += f'''if "{src_field}" in df_transformed_{sanitized_tgt}.columns:
    df_transformed_{sanitized_tgt} = apply_transformations(
        df_transformed_{sanitized_tgt}, 
        "{src_field}", 
        "{transform_logic}"
    )
'''
                if src_field != tgt_field:
                    code += f'''    df_transformed_{sanitized_tgt} = df_transformed_{sanitized_tgt}.withColumnRenamed("{src_field}", "{tgt_field}")
'''
            
            code += f'''log_message("INFO", "  ✓ Transformed {src_field} -> {tgt_field}")

'''
        
        # Add audit columns
        code += f'''
# Add audit columns
df_transformed_{sanitized_tgt} = df_transformed_{sanitized_tgt} \\
    .withColumn("etl_load_timestamp", current_timestamp()) \\
    .withColumn("etl_load_date", current_date()) \\
    .withColumn("etl_source_system", lit("{mapping.get('source_name', 'UNKNOWN')}"))

transformed_dataframes["{tgt_obj}"] = df_transformed_{sanitized_tgt}
log_message("INFO", f"✓ Transformation completed for {tgt_obj}: {{df_transformed_{sanitized_tgt}.count():,}} rows")

'''

    code += '''
# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Data Quality Validation

# COMMAND ----------

if validation_enabled:
    log_message("INFO", "Starting data quality validation...")
    
    validation_results = []
    
'''
    
    for tgt_obj in target_objects.keys():
        sanitized_tgt = _sanitize_name(tgt_obj)
        code += f'''
    # Validate {tgt_obj}
    df_val = transformed_dataframes["{tgt_obj}"]
    
    validation_results.append({{
        "target": "{tgt_obj}",
        "row_count": df_val.count(),
        "column_count": len(df_val.columns),
        "has_duplicates": df_val.count() != df_val.distinct().count()
    }})
    
'''
    
    code += '''
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

'''

    # Generate write logic for each target
    for tgt_obj, tgt_info in target_objects.items():
        tgt_type = tgt_info["type"]
        sanitized_tgt = _sanitize_name(tgt_obj)
        
        code += f'''
# Write to {tgt_obj} ({tgt_type})
log_message("INFO", "Writing to target: {tgt_obj}")
try:
    df_to_write = transformed_dataframes["{tgt_obj}"]
    
'''
        
        if tgt_type == "Delta":
            code += f'''    target_{sanitized_tgt}_path = dbutils.widgets.get("target_{sanitized_tgt}_path")
    
    if write_mode == "merge":
        # Implement Delta merge logic (requires merge key configuration)
        log_message("WARNING", "Merge mode requires merge key configuration - using append instead")
        df_to_write.write \\
            .format("delta") \\
            .mode("append") \\
            .save(target_{sanitized_tgt}_path)
    else:
        df_to_write.write \\
            .format("delta") \\
            .mode(write_mode) \\
            .option("mergeSchema", "true") \\
            .save(target_{sanitized_tgt}_path)
    
    log_message("INFO", f"✓ Successfully wrote to {tgt_obj} (Delta)")
'''
        elif tgt_type == "Parquet":
            code += f'''    target_{sanitized_tgt}_path = dbutils.widgets.get("target_{sanitized_tgt}_path")
    
    df_to_write.write \\
        .format("parquet") \\
        .mode(write_mode) \\
        .save(target_{sanitized_tgt}_path)
    
    log_message("INFO", f"✓ Successfully wrote to {tgt_obj} (Parquet)")
'''
        elif tgt_type == "CSV":
            code += f'''    target_{sanitized_tgt}_path = dbutils.widgets.get("target_{sanitized_tgt}_path")
    
    df_to_write.write \\
        .format("csv") \\
        .option("header", "true") \\
        .mode(write_mode) \\
        .save(target_{sanitized_tgt}_path)
    
    log_message("INFO", f"✓ Successfully wrote to {tgt_obj} (CSV)")
'''
        elif tgt_type == "JDBC":
            code += f'''    jdbc_url = dbutils.widgets.get("target_{sanitized_tgt}_jdbc_url")
    table_name = dbutils.widgets.get("target_{sanitized_tgt}_table")
    username = dbutils.secrets.get(scope=secret_scope, key="jdbc_username")
    password = dbutils.secrets.get(scope=secret_scope, key="jdbc_password")
    
    df_to_write.write \\
        .format("jdbc") \\
        .option("url", jdbc_url) \\
        .option("dbtable", table_name) \\
        .option("user", username) \\
        .option("password", password) \\
        .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \\
        .mode(write_mode) \\
        .save()
    
    log_message("INFO", f"✓ Successfully wrote to {tgt_obj} (JDBC)")
'''
        
        code += f'''    
except Exception as e:
    log_message("ERROR", f"Failed to write to {tgt_obj}: {{str(e)}}")
    raise

'''

    code += '''
# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Final Summary and Statistics

# COMMAND ----------

log_message("INFO", "="*60)
log_message("INFO", "ETL EXECUTION SUMMARY")
log_message("INFO", "="*60)

# Collect statistics
summary_data = []

'''
    
    for tgt_obj in target_objects.keys():
        code += f'''
summary_data.append({{
    "target_object": "{tgt_obj}",
    "source_object": "{source_objects[list(source_objects.keys())[0]]['mappings'][0]['source_object']}",
    "status": "SUCCESS",
    "records_processed": transformed_dataframes["{tgt_obj}"].count()
}})
'''
    
    code += '''
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
# MAGIC - **Auto-scaling**: Enable with min 2, max 8 workers
# MAGIC 
# MAGIC ### Performance Optimization Tips:
# MAGIC 1. **Partitioning**: Consider partitioning Delta tables by date columns
# MAGIC 2. **Caching**: Cache intermediate DataFrames if reused multiple times
# MAGIC 3. **Broadcast Joins**: Use for small lookup tables (<200MB)
# MAGIC 4. **Z-Ordering**: Apply Z-ORDER on frequently filtered columns in Delta tables
# MAGIC 5. **Adaptive Query Execution**: Already enabled in this notebook
# MAGIC 
# MAGIC ### Monitoring and Maintenance:
# MAGIC - Enable Delta table optimizations: `OPTIMIZE table_name`
# MAGIC - Run VACUUM periodically: `VACUUM table_name RETAIN 168 HOURS`
# MAGIC - Monitor Spark UI for bottlenecks
# MAGIC - Set up alerts for job failures
# MAGIC 
# MAGIC ### Security Best Practices:
# MAGIC - Use Azure Key Vault or Databricks Secrets for credentials
# MAGIC - Implement row-level security if required
# MAGIC - Enable audit logging
# MAGIC - Use service principals for production jobs
'''

    return code


def _sanitize_name(name):
    """Sanitize object names for use as variable names"""
    import re
    # Replace non-alphanumeric characters with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # Remove leading digits
    sanitized = re.sub(r'^[0-9]+', '', sanitized)
    # Convert to lowercase
    return sanitized.lower()


def _get_complexity_stats(mappings):
    """Calculate complexity distribution statistics"""
    from collections import Counter
    complexities = [m.get("mapping_complexity", "Unknown") for m in mappings]
    stats = Counter(complexities)
    return dict(stats)


def _deploy_notebook_to_workspace(notebook_path, notebook_code):
    """Deploy generated notebook to Databricks workspace"""
    try:
        databricks_host = os.getenv('DATABRICKS_HOST')
        databricks_token = os.getenv('DATABRICKS_TOKEN')
        
        if not databricks_host or not databricks_token:
            return {
                "success": False,
                "error": "Missing Databricks credentials",
                "message": "Set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables"
            }
        
        # Encode notebook content
        content_b64 = base64.b64encode(notebook_code.encode()).decode()
        
        # API call to import notebook
        url = f"{databricks_host.rstrip('/')}/api/2.0/workspace/import"
        headers = {
            "Authorization": f"Bearer {databricks_token}",
            "Content-Type": "application/json"
        }
        data = {
            "path": notebook_path,
            "format": "SOURCE",
            "language": "PYTHON",
            "content": content_b64,
            "overwrite": True
        }
        
        import requests
        
        # Determine SSL verification setting
        verify_ssl = not SKIP_SSL_VERIFY
        
        response = requests.post(url, headers=headers, json=data, verify=verify_ssl)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Notebook deployed successfully to {notebook_path}",
                "notebook_url": f"{databricks_host}/\#notebook{notebook_path}"
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "message": f"Failed to deploy notebook: {response.text}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to deploy notebook to workspace"
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
