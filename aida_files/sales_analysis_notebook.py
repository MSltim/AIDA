
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
product_sales = sales_df.groupBy("product") \
    .agg(
        sum("amount").alias("revenue"),
        count("*").alias("transactions")
    ) \
    .orderBy(desc("revenue"))

print("Top Products:")
product_sales.show(10)
