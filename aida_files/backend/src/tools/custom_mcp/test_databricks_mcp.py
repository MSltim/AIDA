"""
Test script for Databricks MCP Server
Run this to verify your Databricks MCP setup is working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if environment variables are set"""
    print("=" * 60)
    print("TESTING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    host = os.getenv('DATABRICKS_HOST')
    token = os.getenv('DATABRICKS_TOKEN')
    
    if not host:
        print("❌ DATABRICKS_HOST is not set")
        print("   Set it to your workspace URL (e.g., https://your-workspace.cloud.databricks.com)")
        return False
    else:
        print(f"✅ DATABRICKS_HOST: {host}")
    
    if not token:
        print("❌ DATABRICKS_TOKEN is not set")
        print("   Generate a personal access token in Databricks User Settings")
        return False
    else:
        # Show only first 10 characters for security
        print(f"✅ DATABRICKS_TOKEN: {token[:10]}... (hidden)")
    
    return True

def test_imports():
    """Test if required packages are installed"""
    print("\n" + "=" * 60)
    print("TESTING PYTHON PACKAGES")
    print("=" * 60)
    
    required_packages = {
        'requests': 'requests',
        'dotenv': 'python-dotenv',
        'mcp': 'mcp'
    }
    
    all_installed = True
    for module, package in required_packages.items():
        try:
            if module == 'dotenv':
                __import__('dotenv')
            elif module == 'mcp':
                __import__('mcp.server.fastmcp')
            else:
                __import__(module)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            print(f"   Install it with: pip install {package}")
            all_installed = False
    
    return all_installed

def test_connection():
    """Test connection to Databricks"""
    print("\n" + "=" * 60)
    print("TESTING DATABRICKS CONNECTION")
    print("=" * 60)
    
    try:
        # Import after checking packages
        sys.path.insert(0, os.path.dirname(__file__))
        from Databricks_mcp import DatabricksWorkspaceManagerTool
        
        # Try to list clusters
        print("Attempting to list clusters...")
        result = DatabricksWorkspaceManagerTool(action="list_clusters")
        
        if result.get("success"):
            cluster_count = result.get("data", {}).get("count", 0)
            print(f"✅ Connection successful! Found {cluster_count} cluster(s)")
            
            if cluster_count > 0:
                print("\nYour clusters:")
                for cluster in result["data"]["clusters"]:
                    print(f"  - {cluster['cluster_name']} ({cluster['state']}) - ID: {cluster['cluster_id']}")
            return True
        else:
            print(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
            print(f"   Message: {result.get('message', 'No message')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {str(e)}")
        return False

def test_warehouses():
    """Test listing SQL warehouses"""
    print("\n" + "=" * 60)
    print("TESTING SQL WAREHOUSES")
    print("=" * 60)
    
    try:
        from Databricks_mcp import DatabricksWorkspaceManagerTool
        
        print("Attempting to list SQL warehouses...")
        result = DatabricksWorkspaceManagerTool(action="list_warehouses")
        
        if result.get("success"):
            warehouse_count = result.get("data", {}).get("count", 0)
            print(f"✅ Found {warehouse_count} SQL warehouse(s)")
            
            if warehouse_count > 0:
                print("\nYour SQL warehouses:")
                for warehouse in result["data"]["warehouses"]:
                    print(f"  - {warehouse['name']} ({warehouse['state']}) - ID: {warehouse['id']}")
            return True
        else:
            print(f"❌ Failed to list warehouses: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error listing warehouses: {str(e)}")
        return False

def test_help():
    """Test help command"""
    print("\n" + "=" * 60)
    print("TESTING HELP COMMAND")
    print("=" * 60)
    
    try:
        from Databricks_mcp import DatabricksWorkspaceManagerTool
        
        result = DatabricksWorkspaceManagerTool(action="help")
        
        if result.get("success"):
            print("✅ Help command works")
            return True
        else:
            print("❌ Help command failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing help: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "DATABRICKS MCP SERVER TEST" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    tests = [
        ("Environment Variables", test_environment),
        ("Python Packages", test_imports),
        ("Databricks Connection", test_connection),
        ("SQL Warehouses", test_warehouses),
        ("Help Command", test_help)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("-" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Your Databricks MCP is ready to use!")
        print("\nNext steps:")
        print("1. Configure the MCP in your cline_mcp_settings.json")
        print("2. Restart VS Code or reload the window")
        print("3. Start asking your AI assistant about Databricks!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Run: pip install python-dotenv mcp requests")
        print("- Check your .env file has DATABRICKS_HOST and DATABRICKS_TOKEN")
        print("- Verify your token hasn't expired")
        print("- Ensure your workspace URL is correct")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
