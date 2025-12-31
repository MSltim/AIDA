"""
Test script for Databricks Integration
"""
from databricks_integration import get_databricks_manager

def main():
    print("=" * 60)
    print("Testing Databricks Integration")
    print("=" * 60)
    
    # Get the manager
    print("\n1. Initializing DatabricksManager...")
    db = get_databricks_manager()
    print("   ✅ Manager initialized successfully")
    
    # Test listing clusters
    print("\n2. Testing list_clusters()...")
    result = db.list_clusters()
    if result.get('success'):
        data = result.get('data', {})
        if isinstance(data, dict):
            clusters = data.get('clusters', [])
            count = data.get('count', len(clusters))
            print(f"   ✅ Found {count} clusters")
            for i, cluster in enumerate(clusters[:3], 1):  # Show first 3
                print(f"      {i}. {cluster.get('cluster_name', 'N/A')} - {cluster.get('state', 'N/A')}")
        else:
            print(f"   ⚠️  Unexpected data format")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    
    # Test listing warehouses
    print("\n3. Testing list_warehouses()...")
    result = db.list_warehouses()
    if result.get('success'):
        data = result.get('data', {})
        if isinstance(data, dict):
            warehouses = data.get('warehouses', [])
            print(f"   ✅ Found {len(warehouses)} warehouses")
            for i, wh in enumerate(warehouses[:3], 1):  # Show first 3
                print(f"      {i}. {wh.get('name', 'N/A')} - {wh.get('state', 'N/A')}")
        else:
            print(f"   ⚠️  Unexpected data format")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    
    # Test listing jobs
    print("\n4. Testing list_jobs()...")
    result = db.list_jobs()
    if result.get('success'):
        data = result.get('data', {})
        if isinstance(data, dict):
            jobs = data.get('jobs', [])
            print(f"   ✅ Found {len(jobs)} jobs")
            for i, job in enumerate(jobs[:3], 1):  # Show first 3
                print(f"      {i}. {job.get('settings', {}).get('name', 'N/A')}")
        else:
            print(f"   ⚠️  Unexpected data format")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    
    # Test help
    print("\n5. Testing get_help()...")
    result = db.get_help()
    if result.get('success'):
        print(f"   ✅ Help retrieved successfully")
        # Print first 200 chars of help message
        help_msg = result.get('message', '')
        if help_msg:
            print(f"   📖 {help_msg[:200]}...")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
