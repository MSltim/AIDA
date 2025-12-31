"""Quick debug script to see the actual response structure"""
from databricks_integration import get_databricks_manager
import json

db = get_databricks_manager()

print("=" * 70)
print("Testing list_clusters()")
print("=" * 70)
result = db.list_clusters()
print(json.dumps(result, indent=2, default=str)[:500])

print("\n" + "=" * 70)
print("Testing list_warehouses()")
print("=" * 70)
result = db.list_warehouses()
print(json.dumps(result, indent=2, default=str)[:500])
