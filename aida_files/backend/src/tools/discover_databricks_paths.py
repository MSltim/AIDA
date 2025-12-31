"""
Helper script to find valid Databricks workspace paths
Run this to discover where you can create notebooks
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.tools.databricks_integration import get_databricks_manager


def discover_workspace_paths():
    """Discover valid paths in your Databricks workspace"""
    print("\n" + "="*70)
    print("  DATABRICKS WORKSPACE PATH DISCOVERY")
    print("="*70)
    
    db = get_databricks_manager()
    
    # Try common root paths
    paths_to_check = [
        "/",
        "/Users",
        "/Shared",
        "/Workspace",
        "/Workspace/Users"
    ]
    
    print("\n🔍 Checking for accessible workspace paths...\n")
    
    valid_paths = []
    
    for path in paths_to_check:
        result = db.list_notebooks(path)
        if result.get('success'):
            data = result.get('data', {})
            objects = data.get('objects', [])
            print(f"✅ {path:<25} - Accessible ({len(objects)} items)")
            valid_paths.append(path)
            
            # Show first few items
            if objects:
                for obj in objects[:3]:
                    obj_path = obj.get('path', '')
                    obj_type = obj.get('object_type', '')
                    print(f"   └─ {obj_path} ({obj_type})")
                if len(objects) > 3:
                    print(f"   └─ ... and {len(objects) - 3} more")
        else:
            print(f"❌ {path:<25} - Not accessible")
    
    if valid_paths:
        print("\n" + "="*70)
        print("  RECOMMENDED NOTEBOOK PATHS")
        print("="*70)
        print("\nYou can create notebooks in these locations:")
        for path in valid_paths:
            if path == "/Users":
                print(f"\n📁 {path}/your.email@company.com/")
                print("   Example: /Users/john.doe@company.com/my_notebook")
            elif path == "/Shared":
                print(f"\n📁 {path}/team_folder/")
                print("   Example: /Shared/analytics_team/my_notebook")
            elif path == "/Workspace":
                print(f"\n📁 {path}/your_folder/")
                print("   Example: /Workspace/my_project/my_notebook")
    else:
        print("\n⚠️  No accessible paths found. This might mean:")
        print("   1. You need additional permissions")
        print("   2. The workspace has restricted access")
        print("   3. Contact your Databricks admin for access")
    
    print("\n" + "="*70)
    print("  CREATING NOTEBOOKS")
    print("="*70)
    print("\n💡 To create a notebook, use:")
    print("""
from backend.src.tools.databricks_integration import get_databricks_manager

db = get_databricks_manager()
result = db.create_notebook(
    path="/Users/your.email@company.com/my_notebook",
    content="print('Hello Databricks')",
    language="PYTHON"
)
print(result)
""")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        discover_workspace_paths()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
