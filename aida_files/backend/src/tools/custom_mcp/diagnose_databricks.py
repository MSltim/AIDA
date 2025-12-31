"""
Databricks Connection Diagnostic Tool
Tests connection and credentials step-by-step to identify issues
"""
import os
import requests
from dotenv import load_dotenv, find_dotenv

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

def test_basic_connectivity(host):
    """Test basic network connectivity to Databricks"""
    print_section("STEP 2: Network Connectivity")
    
    try:
        # Just test if we can reach the host
        response = requests.get(host, timeout=10, allow_redirects=True)
        print(f"✅ Can reach Databricks host")
        print(f"   Status: {response.status_code}")
        return True
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("   This might be a certificate issue or proxy problem")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("   Cannot reach the Databricks host")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Cannot connect to Databricks")
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        return False

def test_api_authentication(host, token):
    """Test API authentication"""
    print_section("STEP 3: API Authentication")
    
    url = f"{host}/api/2.0/clusters/list"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing endpoint: {url}")
    print(f"Using token: {token[:10]}...{token[-4:]}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            clusters = data.get('clusters', [])
            print(f"✅ Authentication successful!")
            print(f"   Found {len(clusters)} clusters")
            return True, clusters
        elif response.status_code == 401:
            print(f"❌ Authentication failed (401 Unauthorized)")
            print(f"   Response: {response.text[:200]}")
            print("\n   Possible issues:")
            print("   1. Token is expired or invalid")
            print("   2. Token doesn't have permission for this workspace")
            print("   3. Token format is incorrect")
            return False, None
        elif response.status_code == 403:
            print(f"❌ Access forbidden (403)")
            print(f"   Token is valid but lacks permissions")
            print(f"   Response: {response.text[:200]}")
            return False, None
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None

def test_warehouses(host, token):
    """Test SQL warehouse API"""
    print_section("STEP 4: SQL Warehouses")
    
    url = f"{host}/api/2.0/sql/warehouses"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing endpoint: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            warehouses = data.get('warehouses', [])
            print(f"✅ Can access SQL warehouses!")
            print(f"   Found {len(warehouses)} warehouses")
            
            if warehouses:
                print("\n   Warehouses:")
                for wh in warehouses[:3]:
                    print(f"   - {wh.get('name', 'N/A')} (ID: {wh.get('id', 'N/A')})")
            return True, warehouses
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def provide_recommendations(results):
    """Provide recommendations based on test results"""
    print_section("RECOMMENDATIONS")
    
    env_ok, connectivity_ok, auth_ok, warehouse_ok = results
    
    if not env_ok:
        print("❌ Fix your .env file:")
        print("   1. Ensure DATABRICKS_HOST and DATABRICKS_TOKEN are set")
        print("   2. Remove any quotes around values")
        print("   3. Ensure no extra spaces")
        
    elif not connectivity_ok:
        print("❌ Network connectivity issue:")
        print("   1. Check if you're behind a corporate proxy")
        print("   2. Verify VPN connection if required")
        print("   3. Test host in browser: {host}")
        
    elif not auth_ok:
        print("❌ Authentication issue:")
        print("   1. Regenerate your Databricks access token:")
        print("      - Go to Databricks workspace")
        print("      - User Settings → Access Tokens")
        print("      - Generate new token")
        print("   2. Verify workspace URL is correct")
        print("   3. Ensure token has proper permissions")
        
    elif not warehouse_ok:
        print("⚠️  Cluster access works but warehouse access fails:")
        print("   1. You may not have SQL warehouse permissions")
        print("   2. Create a SQL warehouse in your Databricks workspace")
        print("   3. Request access from your admin")
        
    else:
        print("✅ All tests passed!")
        print("   Your Databricks integration is ready to use")
        print("\n   Next steps:")
        print("   1. Test the integration:")
        print("      python backend/src/tools/test_integration.py")
        print("   2. Start using in your code:")
        print("      from backend.src.tools.databricks_integration import get_databricks_manager")

def main():
    print("\n" + "=" * 70)
    print("  DATABRICKS CONNECTION DIAGNOSTIC TOOL")
    print("=" * 70)
    print("  This tool will help identify connection issues step-by-step")
    print("=" * 70)
    
    # Step 1: Environment variables
    host, token = test_env_variables()
    env_ok = host is not None and token is not None
    
    if not env_ok:
        provide_recommendations((False, False, False, False))
        return
    
    # Step 2: Network connectivity
    connectivity_ok = test_basic_connectivity(host)
    
    if not connectivity_ok:
        provide_recommendations((True, False, False, False))
        return
    
    # Step 3: API authentication
    auth_ok, clusters = test_api_authentication(host, token)
    
    if not auth_ok:
        provide_recommendations((True, True, False, False))
        return
    
    # Step 4: SQL warehouses
    warehouse_ok, warehouses = test_warehouses(host, token)
    
    # Final recommendations
    provide_recommendations((True, True, True, warehouse_ok))
    
    print("\n" + "=" * 70)
    print("  DIAGNOSTIC COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
