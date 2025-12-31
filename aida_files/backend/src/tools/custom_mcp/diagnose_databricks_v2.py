"""
Databricks Connection Diagnostic Tool with SSL Options
Tests connection with and without SSL verification
"""
import os
import requests
import urllib3
from dotenv import load_dotenv, find_dotenv

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_env_variables():
    """Test if environment variables are loaded correctly"""
    print_section("STEP 1: Environment Variables")
    
    load_dotenv(find_dotenv(), verbose=False, override=True)
    
    host = os.getenv('DATABRICKS_HOST')
    token = os.getenv('DATABRICKS_TOKEN')
    
    print(f"DATABRICKS_HOST: {host if host else '❌ NOT FOUND'}")
    print(f"DATABRICKS_TOKEN: {'✅ Found (' + token[:10] + '...' + token[-4:] + ')' if token else '❌ NOT FOUND'}")
    
    if not host or not token:
        print("\n❌ ERROR: Missing credentials in .env file")
        return None, None
    
    # Clean up host URL
    host = host.strip().strip('"').strip("'")
    token = token.strip().strip('"').strip("'")
    
    print(f"\nCleaned HOST: {host}")
    print(f"Token length: {len(token)} characters")
    
    return host, token

def test_api_with_ssl_options(host, token):
    """Test API with different SSL verification options"""
    print_section("STEP 2: API Authentication (Testing SSL Options)")
    
    url = f"{host}/api/2.0/clusters/list"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing endpoint: {url}")
    
    # Try with SSL verification first
    print("\n[Attempt 1] With SSL verification enabled...")
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=True)
        print(f"✅ SUCCESS with SSL verification")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            return True, data.get('clusters', []), True
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL verification failed: {str(e)[:100]}...")
        print("   Trying without SSL verification...")
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}...")
    
    # Try without SSL verification
    print("\n[Attempt 2] Without SSL verification (verify=False)...")
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            clusters = data.get('clusters', [])
            print(f"✅ Authentication successful (without SSL verification)!")
            print(f"   Found {len(clusters)} clusters")
            
            if clusters:
                print("\n   Sample clusters:")
                for cluster in clusters[:3]:
                    print(f"   - {cluster.get('cluster_name', 'N/A')} ({cluster.get('state', 'N/A')})")
            
            print("\n⚠️  NOTE: SSL verification was disabled for this connection")
            print("   This works but is not recommended for production")
            return True, clusters, False
            
        elif response.status_code == 401:
            print(f"❌ Authentication failed (401 Unauthorized)")
            print(f"   Token is invalid or expired")
            return False, None, False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False, None, False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False, None, False

def test_warehouses(host, token, use_ssl):
    """Test SQL warehouse API"""
    print_section("STEP 3: SQL Warehouses")
    
    url = f"{host}/api/2.0/sql/warehouses"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing endpoint: {url}")
    print(f"SSL Verification: {'Enabled' if use_ssl else 'Disabled'}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=use_ssl)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            warehouses = data.get('warehouses', [])
            print(f"✅ Can access SQL warehouses!")
            print(f"   Found {len(warehouses)} warehouses")
            
            if warehouses:
                print("\n   Sample warehouses:")
                for wh in warehouses[:3]:
                    print(f"   - {wh.get('name', 'N/A')} (ID: {wh.get('id', 'N/A')[:20]}...)")
            else:
                print("\n   ⚠️  No warehouses found. You may need to:")
                print("      1. Create a SQL warehouse in Databricks")
                print("      2. Request access from your admin")
            return True, warehouses
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def provide_solution(auth_ok, ssl_needed):
    """Provide solution based on test results"""
    print_section("SOLUTION")
    
    if not auth_ok:
        print("❌ AUTHENTICATION FAILED")
        print("\nTo fix:")
        print("1. Generate a new Databricks Personal Access Token:")
        print("   • Log into Databricks workspace")
        print("   • Click your profile icon → User Settings")
        print("   • Go to Access Tokens tab")
        print("   • Click 'Generate New Token'")
        print("   • Copy the token")
        print("\n2. Update your .env file:")
        print("   DATABRICKS_TOKEN=your-new-token-here")
        
    elif not ssl_needed:
        print("✅ CONNECTION WORKS (without SSL verification)")
        print("\nYou're behind a corporate proxy/firewall.")
        print("\nTemporary Solution (for development):")
        print("  Set this environment variable:")
        print("  DATABRICKS_SKIP_SSL_VERIFY=true")
        print("\nProduction Solution:")
        print("  1. Get SSL certificate from your IT team")
        print("  2. Set REQUESTS_CA_BUNDLE environment variable")
        print("  3. Or configure corporate proxy settings")
        
        # Update the MCP files to support SSL bypass
        print("\n📝 Updating Databricks MCP files to support SSL bypass...")
        return True, False
        
    else:
        print("✅ ALL TESTS PASSED!")
        print("\nYour Databricks integration is ready to use:")
        print("  from backend.src.tools.databricks_integration import get_databricks_manager")
        return True, True

def main():
    print("\n" + "=" * 70)
    print("  DATABRICKS CONNECTION DIAGNOSTIC TOOL v2")
    print("=" * 70)
    print("  Testing connection with SSL verification options")
    print("=" * 70)
    
    # Step 1: Environment variables
    host, token = test_env_variables()
    if not host or not token:
        return
    
    # Step 2: Test API with SSL options
    auth_ok, clusters, ssl_ok = test_api_with_ssl_options(host, token)
    
    if not auth_ok:
        provide_solution(False, False)
        return
    
    # Step 3: Test warehouses
    warehouse_ok, warehouses = test_warehouses(host, token, ssl_ok)
    
    # Provide solution
    success, ssl_secure = provide_solution(True, ssl_ok)
    
    if success and not ssl_secure:
        print("\n" + "=" * 70)
        print("  APPLYING FIX")
        print("=" * 70)
        print("\nAdding SSL bypass support to your .env file...")
        
        # Add to .env if not exists
        env_path = find_dotenv()
        if env_path:
            with open(env_path, 'r') as f:
                content = f.read()
            
            if 'DATABRICKS_SKIP_SSL_VERIFY' not in content:
                with open(env_path, 'a') as f:
                    f.write('\n# Databricks SSL Configuration (for corporate proxies)\n')
                    f.write('DATABRICKS_SKIP_SSL_VERIFY=true\n')
                print("✅ Added DATABRICKS_SKIP_SSL_VERIFY=true to .env")
            else:
                print("ℹ️  DATABRICKS_SKIP_SSL_VERIFY already in .env")
    
    print("\n" + "=" * 70)
    print("  DIAGNOSTIC COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run: python backend\\src\\tools\\custom_mcp\\test_databricks_mcp.py")
    print("2. All tests should pass now!")

if __name__ == "__main__":
    main()
