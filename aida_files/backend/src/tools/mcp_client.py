"""
MCP Client - Unified Tool Management and MCP Server Connection

This module provides complete MCP (Model Context Protocol) tool management with:
  - MCP server configuration and connection (both remote SSE and local STDIO)
  - Tool loading and management from multiple MCP servers
  - JSON-based configuration for Local MCP Servers
  - Integration with Atlassian OAuth via utils.atlassian_oauth module

Configuration:
  - Local MCP Servers are loaded from utils/local_mcp_servers.json
  - Remote MCP Servers can be configured via MCP_PROVIDERS dict
  - Atlassian OAuth is handled by utils.atlassian_oauth module
  - All environment variables are loaded from .env file
"""

import os
import sys
import asyncio
import traceback
import json
from typing import List, Dict, Any, Optional
from dotenv import find_dotenv, load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

# Import OAuth handler from utils
from backend.src.tools.utils.atlassian_oauth import atlassian_oauth

# Load environment variables
src_env = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
if os.path.exists(src_env):
    load_dotenv(src_env)
else:
    load_dotenv(find_dotenv())

def load_enabled_tools() -> Dict[str, Any]:
    """
    Load enabled tools configuration from tools.json.
    Only loads tools that have been explicitly added by the user.
    
    Returns:
        Dict[str, Any]: Dictionary of enabled tool configurations
    """
    tools_path = os.path.join(os.path.dirname(__file__), "tools.json")
    
    if os.path.exists(tools_path):
        try:
            with open(tools_path, "r") as f:
                content = f.read().strip()
                if content:
                    tools = json.loads(content)
                    if tools:  # If tools.json has content
                        print(f"[OK] Loaded {len(tools)} enabled tools from tools.json")
                        return tools
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error parsing tools.json: {e}")
        except Exception as e:
            print(f"[ERROR] Error loading tools.json: {e}")
    
    # Return empty dict if no tools enabled
    print("[INFO] No tools enabled in tools.json - use the sidebar to add tools")
    return {}

def load_all_mcp_servers() -> Dict[str, Any]:
    """
    Load all MCP Servers configuration from mcp_servers.json.
    
    Returns:
        Dict[str, Any]: Dictionary of all MCP server configurations
    """
    config_path = os.path.join(os.path.dirname(__file__), "utils", "mcp_servers.json")
    
    if not os.path.exists(config_path):
        print(f"[WARN] MCP Servers config not found at: {config_path}")
        return {}
    
    try:
        with open(config_path, "r") as f:
            servers = json.load(f)
        print(f"[OK] Loaded {len(servers)} MCP server configurations from mcp_servers.json")
        return servers
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parsing mcp_servers.json: {e}")
        return {}
    except Exception as e:
        print(f"[ERROR] Error loading mcp_servers.json: {e}")
        return {}


# Load enabled tools (from tools.json or fallback to mcp_servers.json)
LOCAL_MCP_SERVERS = load_enabled_tools()


# =============================================================================
# MCP PROVIDER CONFIGURATIONS
# =============================================================================

MCP_PROVIDERS = {}


# =============================================================================
# MCP CLIENT MANAGER
# =============================================================================

class MCPClientManager:
    """
    MCP-Compatible Client Manager for connecting to any MCP Server.
    
    Similar to Claude Desktop, GitHub Copilot, Docker MCP Toolkit.
    Supports both remote (SSE) and local (STDIO) MCP servers.
    """
    
    def __init__(self):
        self.servers_config: Dict[str, Any] = {}
        self.client: Optional[MultiServerMCPClient] = None
        self.tools: List[BaseTool] = []
        self._configured = False
    
    async def configure(self) -> "MCPClientManager":
        """Configure all MCP providers"""
        print("\n" + "="*60)
        print("[CONFIG] MCP CLIENT - Configuring Providers")
        print("="*60)
        
        # Configure remote MCP servers (SSE)
        await self._configure_remote_servers()
        
        # Configure local MCP servers (STDIO)
        self._configure_local_servers()
        
        if not self.servers_config:
            print("\n[WARN] No MCP servers configured!")
            print("  Set tokens in .env or enable local servers")
        
        self.client = MultiServerMCPClient(self.servers_config)
        self._configured = True
        return self
    
    async def _configure_remote_servers(self):
        """Configure remote MCP servers with SSE transport"""
        print("\n[REMOTE] Remote MCP Servers:")
        
        for provider_id, config in MCP_PROVIDERS.items():
            if not config.get("enabled", False):
                print(f"  [SKIP] {config['name']} - disabled")
                continue
            
            # Handle OAuth-based providers
            if config.get("oauth"):
                if provider_id == "atlassian":
                    # Check if token is already cached and valid
                    if atlassian_oauth.is_token_valid():
                        token = atlassian_oauth.access_token
                        print(f"  [OK] {config['name']} - using cached token")
                    else:
                        token = await atlassian_oauth.get_access_token()
                        if not token:
                            print(f"  [WARN] {config['name']} - OAuth failed")
                            continue
                else:
                    print(f"  [WARN] {config['name']} - OAuth not implemented for this provider")
                    continue
            else:
                # Static token from environment
                token = os.getenv(config.get("token_env", ""))
                if not token:
                    print(f"  [WARN] {config['name']} - no token")
                    print(f"     Set {config.get('token_env')} in .env")
                    continue
            
            self.servers_config[provider_id] = {
                "url": config["mcp_url"],
                "transport": config.get("transport", "sse"),
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "Accept": "text/event-stream"
                }
            }
            print(f"  [OK] {config['name']} - configured")
    
    def _configure_local_servers(self):
        """Configure local MCP servers with STDIO transport"""
        print("\n[LOCAL] Local MCP Servers:")
        
        # Reload enabled tools from tools.json each time
        enabled_tools = load_enabled_tools()
        
        base_path = os.path.dirname(os.path.dirname(__file__))  # tools folder
        
        for server_id, config in enabled_tools.items():
            if not config.get("enabled", False):
                print(f"  [SKIP] {config['name']} - disabled")
                continue
            
            # Check if it's a command-based server (like mcp-remote, azure-devops, exa)
            if "command" in config:
                # Handle args_template with environment variable substitution
                if "args_template" in config:
                    args = []
                    env_vars = config.get("env_vars", {})
                    missing_vars = []
                    
                    for arg in config["args_template"]:
                        # Check if arg contains a placeholder like {ado_org}
                        if "{" in arg and "}" in arg:
                            # Extract placeholder name
                            placeholder = arg[arg.find("{")+1:arg.find("}")]
                            env_var_name = env_vars.get(placeholder, placeholder.upper())
                            env_value = os.getenv(env_var_name)
                            
                            if env_value:
                                # Replace placeholder with environment variable value
                                args.append(arg.replace("{" + placeholder + "}", env_value))
                            else:
                                missing_vars.append(env_var_name)
                        else:
                            args.append(arg)
                    
                    if missing_vars:
                        print(f"  [WARN] {config['name']} - missing env vars: {', '.join(missing_vars)}")
                        print(f"     Please set these in your .env file")
                        continue
                else:
                    args = config.get("args", [])
                
                # Build server config
                # Resolve relative paths for command-based servers
                command = config["command"]
                if not os.path.isabs(command) and not command.startswith(("npx", "node", "python")):
                    # If it's a relative path, resolve it from base_path
                    command = os.path.join(base_path, command)
                
                server_config = {
                    "transport": "stdio",
                    "command": command,
                    "args": args,
                }
                
                # Handle env configuration for passing environment variables to subprocess
                if "env" in config:
                    env_config = {}
                    missing_env = []
                    for env_key, env_value in config["env"].items():
                        # Check if value is a placeholder like {EXA_API_KEY}
                        if env_value.startswith("{") and env_value.endswith("}"):
                            actual_env_var = env_value[1:-1]  # Remove { and }
                            actual_value = os.getenv(actual_env_var)
                            if actual_value:
                                env_config[env_key] = actual_value
                            else:
                                missing_env.append(actual_env_var)
                        else:
                            env_config[env_key] = env_value
                    
                    if missing_env:
                        print(f"  [WARN] {config['name']} - missing env vars: {', '.join(missing_env)}")
                        print(f"     Please set these in your .env file")
                        continue
                    
                    server_config["env"] = env_config
                
                self.servers_config[server_id] = server_config
                print(f"  [OK] {config['name']} - configured (command: {config['command']})")
            # Or a script-based server
            elif "script" in config:
                script_path = os.path.join(base_path, config["script"])
                if not os.path.exists(script_path):
                    print(f"  [WARN] {config['name']} - script not found at {script_path}")
                    continue
                
                # Get the Python executable from the current environment
                # This ensures the subprocess uses the same venv/environment
                python_executable = sys.executable
                
                self.servers_config[server_id] = {
                    "transport": "stdio",
                    "command": python_executable,
                    "args": [script_path],
                }
                print(f"  [OK] {config['name']} - configured (python: {python_executable})")
    
    async def connect(self) -> List[BaseTool]:
        """Connect to all configured MCP servers and get tools"""
        if not self._configured:
            await self.configure()
        
        if not self.servers_config:
            print("\n[WARN] No MCP servers to connect to!")
            return []
        
        print("\n[CONNECTING] Connecting to MCP servers...")
        print(f"   Servers: {list(self.servers_config.keys())}")
        
        # Try connecting to servers one by one to identify which ones fail
        all_tools = []
        failed_servers = []
        successful_servers = []
        
        for server_id, server_config in self.servers_config.items():
            try:
                print(f"   Connecting to {server_id}...", end=" ")
                single_client = MultiServerMCPClient({server_id: server_config})
                
                async with asyncio.timeout(30):  # 30 second timeout per server
                    server_tools = await single_client.get_tools()
                
                all_tools.extend(server_tools)
                successful_servers.append(server_id)
                print(f"[OK] ({len(server_tools)} tools)")
                
            except asyncio.TimeoutError:
                print(f"[FAIL] timeout")
                failed_servers.append((server_id, "Connection timeout after 30 seconds"))
            except ExceptionGroup as eg:
                error_msg = self._get_exception_message(eg)
                print(f"[FAIL] {error_msg}")
                failed_servers.append((server_id, error_msg))
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                print(f"[FAIL] {error_msg}")
                failed_servers.append((server_id, error_msg))
        
        # Summary
        print(f"\n[SUMMARY] Connection Summary:")
        print(f"   [OK] Successful: {len(successful_servers)} servers")
        if successful_servers:
            print(f"     {', '.join(successful_servers)}")
        print(f"   [FAIL] Failed: {len(failed_servers)} servers")
        for server_id, error in failed_servers:
            print(f"     - {server_id}: {error}")
        
        self.tools = all_tools
        print(f"\n[OK] Total tools loaded: {len(self.tools)}")
        return self.tools
    
    def _get_exception_message(self, eg) -> str:
        """Extract the root error message from an ExceptionGroup"""
        for exc in eg.exceptions:
            if isinstance(exc, ExceptionGroup):
                return self._get_exception_message(exc)
            else:
                return f"{type(exc).__name__}: {str(exc)[:80]}"
        return "Unknown error"
    
    async def list_tools(self) -> List[BaseTool]:
        """List all available tools with details"""
        if not self.tools:
            await self.connect()
        
        if self.tools:
            print("\n" + "="*60)
            print("[TOOLS] AVAILABLE MCP TOOLS")
            print("="*60)
            
            for i, tool in enumerate(self.tools, 1):
                print(f"\n{i}. {tool.name}")
                if hasattr(tool, 'description') and tool.description:
                    desc = tool.description[:150] + "..." if len(tool.description) > 150 else tool.description
                    print(f"   {desc}")
        
        return self.tools
    
    async def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a specific tool by name"""
        if not self.tools:
            await self.connect()
        
        for tool in self.tools:
            if tool.name == tool_name:
                print(f"\n[TOOL] Calling tool: {tool_name}")
                result = await tool.ainvoke(kwargs)
                return result
        
        print(f"[FAIL] Tool not found: {tool_name}")
        return None
    
    def get_tools_for_agent(self) -> List[BaseTool]:
        """Get tools list for use with LangChain agents"""
        return self.tools


# Global MCP Client Manager Instance
mcp_client_manager = MCPClientManager()


# =============================================================================
# Public API - Main Functions for Tool Access
# =============================================================================

def reload_tool_config():
    """
    Reload tool configuration from tools.json.
    Call this when tools are added/removed via the API.
    """
    global LOCAL_MCP_SERVERS
    LOCAL_MCP_SERVERS = load_enabled_tools()
    # Reset the client manager to force reconfiguration
    mcp_client_manager._configured = False
    mcp_client_manager.servers_config = {}
    mcp_client_manager.tools = []
    print("[OK] Tool configuration reloaded")

async def load_all_tools() -> List[BaseTool]:
    """
    Load and return all configured MCP tools.
    
    This is the main entry point for loading tools.
    
    Returns:
        List[BaseTool]: List of all available MCP tools
    
    Example:
        tools = await load_all_tools()
        for tool in tools:
            print(f"Tool: {tool.name}")
    """
    # Reload config to pick up any changes
    reload_tool_config()
    return await mcp_client_manager.connect()


async def get_available_tools() -> List[BaseTool]:
    """
    Get all available tools (alias for load_all_tools).
    
    Returns:
        List[BaseTool]: List of all available MCP tools
    """
    return await load_all_tools()


def get_tools_for_agent() -> List[BaseTool]:
    """
    Get tools list for use with LangChain agents.
    
    Note: Must be called after tools have been loaded with load_all_tools().
    
    Returns:
        List[BaseTool]: List of tools for agents
    """
    return mcp_client_manager.get_tools_for_agent()


# =============================================================================
# CLI Entry Point - For Testing and Debugging
# =============================================================================

async def main():
    """Main entry point for CLI usage"""
    print("\n" + "="*60)
    print("[LOADER] MCP TOOLS - Tool Loader")
    print("   Loading all configured MCP servers and tools")
    print("="*60)
    
    try:
        tools = await mcp_client_manager.list_tools()
        
        if tools:
            print("\n" + "-"*60)
            print("[TIP] Usage in Code:")
            print("   from backend.src.tools.mcp_client import load_all_tools")
            print("   tools = await load_all_tools()")
            print("   for tool in tools:")
            print("       print(f'Tool: {tool.name}')")
            print("-"*60)
        else:
            print("\n[WARN] No tools loaded. Check your MCP server configuration.")
    
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
