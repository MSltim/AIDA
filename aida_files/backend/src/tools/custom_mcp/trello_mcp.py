import ast
import json
import os
import re
import time
import requests
from datetime import datetime
from typing import List, Dict, Any

from typing import List, Dict


from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP
import numpy as np
import pandas as pd


load_dotenv(find_dotenv(), verbose=True, override=True)


mcp = FastMCP("Trello MCP", "0.1.0")

# Helper function to validate environment variables
def _validate_trello_env() -> dict:
    """Validate required Trello environment variables."""
    try:
        return {
            "api_key": os.environ['TRELLO_API_KEY'],
            "api_token": os.environ['TRELLO_API_TOKEN'],
            "board_id": os.environ['TRELLO_BOARD_ID'],
            "base_url": os.getenv('DLAI_TRELLO_BASE_URL', 'https://api.trello.com')
        }
    except KeyError as e:
        return {"error": f"Missing environment variable: {e}"}

# Helper function to make Trello API requests
def _make_trello_request(url: str, params: dict) -> dict:
    """Make a Trello API request and return structured response."""
    try:
        response = requests.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json(),
            "error": None
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "data": None,
            "error": f"API request failed: {str(e)}"
        }

# Project Board Data Fetcher Tool
@mcp.tool()
def GetAllBoardCards() -> dict:
    """
    Retrieves all cards from the project management board.
    
    Returns: dict - Structured response with success status, cards data, and any error messages.
    """
    env_vars = _validate_trello_env()
    if "error" in env_vars:
        return {
            "success": False,
            "data": None,
            "error": env_vars["error"],
            "message": "Please ensure TRELLO_API_KEY, TRELLO_API_TOKEN, and TRELLO_BOARD_ID are set."
        }
    
    url = f"{env_vars['base_url']}/1/boards/{env_vars['board_id']}/cards"
    params = {
        'key': env_vars['api_key'],
        'token': env_vars['api_token'],
        'fields': 'name,idList,due,dateLastActivity,labels,desc',
        'attachments': 'true',
        'actions': 'commentCard'
    }
    
    result = _make_trello_request(url, params)
    if result["success"]:
        return {
            "success": True,
            "data": {
                "cards": result["data"],
                "total_cards": len(result["data"])
            },
            "error": None,
            "message": f"Retrieved {len(result['data'])} cards from the board."
        }
    else:
        return {
            "success": False,
            "data": None,
            "error": result["error"],
            "message": "Failed to retrieve board cards."
        }

# Get Card Details Tool
@mcp.tool()
def GetCardDetails(card_id: str) -> dict:
    """
    Retrieves detailed information about a specific card/task.
    
    Args:
        card_id (str): The unique identifier of the card to fetch.
    
    Returns: dict - Structured response with card details or error information.
    """
    if not card_id:
        return {
            "success": False,
            "data": None,
            "error": "Missing required parameter: card_id",
            "message": "Please provide a valid card ID."
        }
    
    env_vars = _validate_trello_env()
    if "error" in env_vars:
        return {
            "success": False,
            "data": None,
            "error": env_vars["error"],
            "message": "Please ensure TRELLO_API_KEY, TRELLO_API_TOKEN, and TRELLO_BOARD_ID are set."
        }
    
    url = f"{env_vars['base_url']}/1/cards/{card_id}"
    params = {
        'key': env_vars['api_key'],
        'token': env_vars['api_token']
    }
    
    result = _make_trello_request(url, params)
    if result["success"]:
        return {
            "success": True,
            "data": {
                "card": result["data"]
            },
            "error": None,
            "message": f"Retrieved details for card: {result['data'].get('name', 'Unknown')}"
        }
    else:
        return {
            "success": False,
            "data": None,
            "error": result["error"],
            "message": f"Failed to retrieve card details for ID: {card_id}"
        }

# Get Board Columns Tool
@mcp.tool()
def GetBoardColumns() -> dict:
    """
    Retrieves all available columns/lists from the project board.
    
    Returns: dict - Structured response with columns data or error information.
    """
    env_vars = _validate_trello_env()
    if "error" in env_vars:
        return {
            "success": False,
            "data": None,
            "error": env_vars["error"],
            "message": "Please ensure TRELLO_API_KEY, TRELLO_API_TOKEN, and TRELLO_BOARD_ID are set."
        }
    
    url = f"{env_vars['base_url']}/1/boards/{env_vars['board_id']}/lists"
    params = {
        'key': env_vars['api_key'],
        'token': env_vars['api_token'],
        'fields': 'id,name,pos'
    }
    
    result = _make_trello_request(url, params)
    if result["success"]:
        columns = [{"id": col["id"], "name": col["name"], "position": col["pos"]} for col in result["data"]]
        return {
            "success": True,
            "data": {
                "columns": columns,
                "total_columns": len(columns)
            },
            "error": None,
            "message": f"Found {len(columns)} columns on the board."
        }
    else:
        return {
            "success": False,
            "data": None,
            "error": result["error"],
            "message": "Failed to retrieve board columns."
        }

# Create Board Card Tool
@mcp.tool()
def CreateBoardCard(title: str, description: str, column_name: str, due_date: str = None) -> dict:
    """
    Creates a new card in the specified board column.
    
    Args:
        title (str): The title of the card to create.
        description (str): The description/content of the card.
        column_name (str): The name of the column to place the card in.
        due_date (str, optional): Due date in YYYY-MM-DD format.
    
    Returns: dict - Structured response with card creation status and details.
    """
    # Validate required parameters
    if not title or not description or not column_name:
        return {
            "success": False,
            "data": None,
            "error": "Missing required parameters",
            "message": "Please provide title, description, and column_name."
        }
    
    env_vars = _validate_trello_env()
    if "error" in env_vars:
        return {
            "success": False,
            "data": None,
            "error": env_vars["error"],
            "message": "Please ensure TRELLO_API_KEY, TRELLO_API_TOKEN, and TRELLO_BOARD_ID are set."
        }
    
    # First, get the column ID by name
    columns_result = GetBoardColumns()
    if not columns_result["success"]:
        return {
            "success": False,
            "data": None,
            "error": "Failed to retrieve board columns",
            "message": columns_result.get("message", "Unable to access board columns.")
        }
    
    # Find the target column
    target_column_id = None
    available_columns = []
    for column in columns_result["data"]["columns"]:
        available_columns.append(column["name"])
        if column["name"].lower() == column_name.lower():
            target_column_id = column["id"]
            break
    
    if not target_column_id:
        return {
            "success": False,
            "data": None,
            "error": f"Column '{column_name}' not found",
            "message": f"Available columns: {', '.join(available_columns)}"
        }
    
    # Prepare card data
    card_data = {
        'idList': target_column_id,
        'name': title,
        'desc': description,
        'key': env_vars['api_key'],
        'token': env_vars['api_token']
    }
    
    # Add due date if provided
    if due_date:
        try:
            from datetime import datetime
            due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
            card_data['due'] = due_datetime.isoformat() + "Z"
        except ValueError:
            return {
                "success": False,
                "data": None,
                "error": "Invalid due date format",
                "message": "Due date must be in YYYY-MM-DD format (e.g., '2024-12-01')."
            }
    
    # Create the card
    url = f"{env_vars['base_url']}/1/cards"
    try:
        response = requests.post(url, json=card_data, timeout=10, verify=False)
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "data": {
                "card_id": result.get("id"),
                "card_title": result.get("name"),
                "card_url": result.get("url"),
                "column_name": column_name,
                "due_date": due_date
            },
            "error": None,
            "message": f"Card '{title}' created successfully in column '{column_name}'."
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to create card: {str(e)}",
            "message": "Unable to create the card. Please check your connection and try again."
        }

# Create Board Column Tool
@mcp.tool()
def CreateBoardColumn(column_name: str, position: str = "bottom") -> dict:
    """
    Creates a new column/list on the project board.
    
    Args:
        column_name (str): The name of the new column to create.
        position (str, optional): Position of the column ("top", "bottom", or specific position number).
    
    Returns: dict - Structured response with column creation status and details.
    """
    if not column_name:
        return {
            "success": False,
            "data": None,
            "error": "Missing required parameter: column_name",
            "message": "Please provide a valid column name."
        }
    
    env_vars = _validate_trello_env()
    if "error" in env_vars:
        return {
            "success": False,
            "data": None,
            "error": env_vars["error"],
            "message": "Please ensure TRELLO_API_KEY, TRELLO_API_TOKEN, and TRELLO_BOARD_ID are set."
        }
    
    # Prepare column data
    column_data = {
        'name': column_name,
        'idBoard': env_vars['board_id'],
        'key': env_vars['api_key'],
        'token': env_vars['api_token']
    }
    
    # Set position
    if position.lower() == "top":
        column_data['pos'] = "top"
    elif position.lower() == "bottom":
        column_data['pos'] = "bottom"
    else:
        # Try to parse as number
        try:
            pos_num = int(position)
            column_data['pos'] = pos_num
        except ValueError:
            column_data['pos'] = "bottom"  # Default fallback
    
    # Create the column
    url = f"{env_vars['base_url']}/1/lists"
    try:
        response = requests.post(url, json=column_data, timeout=10, verify=False)
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "data": {
                "column_id": result.get("id"),
                "column_name": result.get("name"),
                "position": result.get("pos"),
                "board_id": result.get("idBoard")
            },
            "error": None,
            "message": f"Column '{column_name}' created successfully."
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to create column: {str(e)}",
            "message": "Unable to create the column. Please check your connection and try again."
        }

# Move Card Tool
@mcp.tool()
def MoveCard(card_id: str, target_column_name: str) -> dict:
    """
    Moves a card to a different column (changes card status/stage).
    
    Args:
        card_id (str): The ID of the card to move.
        target_column_name (str): The name of the column to move the card to.
    
    Returns: dict - Structured response with move operation status and details.
    """
    if not card_id or not target_column_name:
        return {
            "success": False,
            "data": None,
            "error": "Missing required parameters",
            "message": "Please provide card_id and target_column_name."
        }
    
    env_vars = _validate_trello_env()
    if "error" in env_vars:
        return {
            "success": False,
            "data": None,
            "error": env_vars["error"],
            "message": "Please ensure TRELLO_API_KEY, TRELLO_API_TOKEN, and TRELLO_BOARD_ID are set."
        }
    
    # First, get the target column ID by name
    columns_result = GetBoardColumns()
    if not columns_result["success"]:
        return {
            "success": False,
            "data": None,
            "error": "Failed to retrieve board columns",
            "message": columns_result.get("message", "Unable to access board columns.")
        }
    
    # Find the target column
    target_column_id = None
    available_columns = []
    for column in columns_result["data"]["columns"]:
        available_columns.append(column["name"])
        if column["name"].lower() == target_column_name.lower():
            target_column_id = column["id"]
            break
    
    if not target_column_id:
        return {
            "success": False,
            "data": None,
            "error": f"Column '{target_column_name}' not found",
            "message": f"Available columns: {', '.join(available_columns)}"
        }
    
    # Move the card
    url = f"{env_vars['base_url']}/1/cards/{card_id}"
    card_data = {
        'idList': target_column_id,
        'key': env_vars['api_key'],
        'token': env_vars['api_token']
    }
    
    try:
        response = requests.put(url, json=card_data, timeout=10, verify=False)
        response.raise_for_status()
        result = response.json()
        
        return {
            "success": True,
            "data": {
                "card_id": result.get("id"),
                "card_name": result.get("name"),
                "new_column_id": result.get("idList"),
                "target_column_name": target_column_name
            },
            "error": None,
            "message": f"Card moved successfully to column '{target_column_name}'."
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to move card: {str(e)}",
            "message": "Unable to move the card. Please check the card ID and try again."
        }

# Update Card Status Tool
@mcp.tool()
def UpdateCardStatus(card_id: str, new_status: str) -> dict:
    """
    Updates a card's status by moving it to the appropriate column.
    Common statuses: "To Do", "In Progress", "Done", "Backlog", "Review", etc.
    
    Args:
        card_id (str): The ID of the card to update.
        new_status (str): The new status (column name) for the card.
    
    Returns: dict - Structured response with status update operation details.
    """
    # This is essentially an alias for MoveCard with clearer naming for status updates
    return MoveCard(card_id, new_status)

if __name__ == "__main__":
    
    mcp.run(transport="stdio")