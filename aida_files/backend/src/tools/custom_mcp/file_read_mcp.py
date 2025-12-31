import os
from typing import Dict

from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv(find_dotenv(), verbose=True, override=True)


mcp = FastMCP("File Tools MCP", "0.1.0")


# File Read Tool
@mcp.tool()
def FileReadTool(file_path: str) -> str:
    """
    Reads the content of a file and returns it as a string.

    Description:
        - File Reading: Opens and reads the content of a specified file.
        - Content Retrieval: Returns the entire file content as a string for downstream processing.
        - Supports Templates: Useful for loading predefined templates or configuration files.

    Arguments:
        file_path (str): The path to the file that needs to be read.

    Returns:
        str: The content of the file as a string.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


if __name__ == "__main__":
    
    mcp.run(transport="stdio")
