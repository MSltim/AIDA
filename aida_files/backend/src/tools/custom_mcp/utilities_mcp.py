import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Any

from langchain_community.tools import DuckDuckGoSearchResults

from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv(find_dotenv(), verbose=True, override=True)


mcp = FastMCP("Utilities MCP", "0.1.0")

# Current Date Tool
@mcp.tool()
def CurrentDateTool() -> str:
    """
    Description: Current Date and Time Provider - Returns today's date and current timestamp for scheduling, planning, and time-based operations.
    Use this when you need to set due dates, create timestamps, schedule tasks, or perform any date-related calculations for project management.
    
    Arguments: None
    
    Returns: str - Today's date and current time formatted as 'DD-MMM-YYYY HH:MM:SS' (e.g., '29-Oct-2025 14:30:45').
    """
    return time.strftime("%d-%b-%Y %H:%M:%S")

# Internet Search Tool
@mcp.tool()
def InternetSearchTool(query: str):
    """
    Internet/Web Search Tool - Retrieves relevant web search results using DuckDuckGo.

    Description:
    This tool performs a web search using DuckDuckGo and returns a list of summarized results.
    It is useful for agents that need to gather up-to-date information from the internet
    without relying on traditional search engines. The results include titles, snippets, and URLs.

    Arguments:
    - query (str): The search query string to look up.

    Returns:
    - List[Dict]: A list of dictionaries containing search result metadata such as title, snippet, and URL.
    """
    try:
        duckduckgo_tool = DuckDuckGoSearchResults()
        return duckduckgo_tool.run(query)
    except Exception as e:
        return {"error": f"InternetSearchTool failed: {str(e)}. If this is a certificate error, please check your system's CA certificates or use a trusted network."}


if __name__ == "__main__":
    
    mcp.run(transport="stdio")
