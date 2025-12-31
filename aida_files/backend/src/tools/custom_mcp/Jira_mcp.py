import os
import requests
from typing import Dict

from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv(find_dotenv(), verbose=True, override=True)


mcp = FastMCP("MCP Tools Server", "0.1.0")

# JIRA Project Manager Tool
@mcp.tool()
def JiraProjectManagerTool(
    action: str,
    project_name: str = None,
    project_key: str = None,
    issue_title: str = None,
    issue_description: str = None,
    issue_type: str = None,
    priority: str = None,
    assignee: str = None
) -> dict:
    """
    JIRA Project Manager Tool - Manage JIRA projects, issues, and project information.
    
    This tool provides a unified interface for JIRA project management operations including:
    - Fetch project details and project IDs
    - List all available projects in the JIRA instance
    - Create issues/tickets in specified projects
    - Retrieve project information and metadata
    - Provide usage guidance and error handling
    
    The tool automatically handles JIRA API authentication, project validation, 
    and provides structured responses for all operations.
    
    Args:
        action (str): The action to perform. Options:
            - "list_projects": Show all available JIRA projects
            - "get_project": Get details for a specific project by name/key
            - "create_issue": Create a new issue in a specified project
            - "help" or "guide": Show usage instructions and available projects
            
        project_name (str, optional): The name of the JIRA project (e.g., "My Project")
        project_key (str, optional): The key of the JIRA project (e.g., "MP", "DEMO")
        issue_title (str, optional): The title/summary of the issue (required for create_issue)
        issue_description (str, optional): Detailed description of the issue (required for create_issue)
        issue_type (str, optional): Type of issue (e.g., "Task", "Bug", "Story")
        priority (str, optional): Priority level (e.g., "High", "Medium", "Low")
        assignee (str, optional): Email or username of the assignee
    
    Returns:
        dict: Standardized response with success status, data, and messages
    
    Examples:
        # List all available JIRA projects
        JiraProjectManagerTool(action="list_projects")
        
        # Get specific project details
        JiraProjectManagerTool(
            action="get_project",
            project_name="My Project",
            project_key="MP"
        )
        
        # Create a new issue
        JiraProjectManagerTool(
            action="create_issue",
            project_key="MP",
            issue_title="Fix login bug",
            issue_description="Users cannot log in due to authentication error",
            issue_type="Bug",
            priority="High"
        )
        
        # Get help and see available options
        JiraProjectManagerTool(action="help")
    """
    
    # Validate required environment variables
    try:
        jira_api_key = os.environ['JIRA_API_KEY']
        user_email_id = os.environ['JIRA_API_USER_EMAIL_ID']
        jira_base_url = os.getenv('JIRA_BASE_URL')
        
        if not jira_base_url:
            return {
                "success": False,
                "error": "Missing environment variable: JIRA_BASE_URL",
                "message": "Please ensure JIRA_BASE_URL is set in your environment."
            }
            
    except KeyError as e:
        return {
            "success": False,
            "error": f"Missing environment variable: {e}",
            "message": "Please ensure JIRA_API_KEY, JIRA_API_USER_EMAIL_ID, and JIRA_BASE_URL are set in your environment."
        }
    
    # Normalize action parameter
    action = action.lower().strip()
    
    # Helper function to extract project ID
    def _extract_project_id(projects, target_name=None, target_key=None):
        """Extract project ID by project name or key"""
        for project in projects:
            if (project.get("name") == target_name) and (project.get("key") == target_key):
                return project.get("id")
        return None
    
    # Helper function to make JIRA API requests
    def _make_jira_request(endpoint, method="GET", data=None):
        """Make authenticated JIRA API request"""
        url = f"{jira_base_url.rstrip('/')}/rest/api/2/{endpoint}"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        auth = requests.auth.HTTPBasicAuth(user_email_id, jira_api_key)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, auth=auth, verify=False)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, auth=auth, json=data, verify=False)
            else:
                return None, {"error": f"Unsupported HTTP method: {method}"}
            
            return response, None
        except Exception as e:
            return None, {"error": f"Request failed: {str(e)}"}
    
    # Action: List all projects
    if action in ["list_projects", "show_projects", "projects", "list"]:
        try:
            response, error = _make_jira_request("project")
            if error:
                return {
                    "success": False,
                    "action": "list_projects",
                    "error": error["error"],
                    "message": "Failed to fetch JIRA projects."
                }
            
            if response.status_code == 200:
                projects = response.json()
                
                return {
                    "success": True,
                    "action": "list_projects",
                    "data": {
                        "projects": projects,
                        "count": len(projects)
                    },
                    "message": f"Found {len(projects)} JIRA projects."
                }
            else:
                return {
                    "success": False,
                    "action": "list_projects",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to fetch projects. Status: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "action": "list_projects",
                "error": str(e),
                "message": "An unexpected error occurred while fetching projects."
            }
    
    # Action: Get specific project details
    elif action in ["get_project", "project_details", "project_info", "fetch_project"]:
        if not project_name or not project_key:
            return {
                "success": False,
                "action": "get_project",
                "error": "Missing required parameters",
                "message": "Please provide both project_name and project_key to fetch project details.",
                "usage": "JiraProjectManagerTool(action='get_project', project_name='Project Name', project_key='PROJ')"
            }
        
        try:
            # First get all projects to find the specific one
            response, error = _make_jira_request("project")
            if error:
                return {
                    "success": False,
                    "action": "get_project",
                    "error": error["error"],
                    "message": "Failed to fetch JIRA projects."
                }
            
            if response.status_code == 200:
                projects = response.json()
                project_id = _extract_project_id(projects, project_name, project_key)
                
                if project_id:
                    # Find the full project details
                    target_project = None
                    for project in projects:
                        if project.get("id") == project_id:
                            target_project = project
                            break
                    
                    return {
                        "success": True,
                        "action": "get_project",
                        "data": {
                            "project_id": project_id,
                            "project_details": target_project
                        },
                        "message": f"Successfully found project '{project_name}' with ID: {project_id}"
                    }
                else:
                    available_projects = [f"{p.get('name')} ({p.get('key')})" for p in projects[:5]]
                    return {
                        "success": False,
                        "action": "get_project",
                        "error": "Project not found",
                        "message": f"Project '{project_name}' with key '{project_key}' not found.",
                        "hint": f"Available projects (first 5): {', '.join(available_projects)}...",
                        "suggestion": "Use JiraProjectManagerTool(action='list_projects') to see all available projects."
                    }
            else:
                return {
                    "success": False,
                    "action": "get_project",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to fetch projects. Status: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "action": "get_project",
                "error": str(e),
                "message": "An unexpected error occurred while fetching project details."
            }
    
    # Action: Create issue
    elif action in ["create_issue", "new_issue", "add_issue", "create_ticket"]:
        if not all([project_key, issue_title, issue_description]):
            return {
                "success": False,
                "action": "create_issue",
                "error": "Missing required parameters",
                "message": "Please provide project_key, issue_title, and issue_description to create an issue.",
                "usage": "JiraProjectManagerTool(action='create_issue', project_key='PROJ', issue_title='Title', issue_description='Description')"
            }
        
        try:
            # Prepare issue data
            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": issue_title,
                    "description": issue_description,
                    "issuetype": {"name": issue_type or "Task"}
                }
            }
            
            # Add optional fields
            if priority:
                issue_data["fields"]["priority"] = {"name": priority}
            if assignee:
                issue_data["fields"]["assignee"] = {"name": assignee}
            
            response, error = _make_jira_request("issue", method="POST", data=issue_data)
            if error:
                return {
                    "success": False,
                    "action": "create_issue",
                    "error": error["error"],
                    "message": "Failed to create JIRA issue."
                }
            
            if response.status_code == 201:
                issue_result = response.json()
                issue_key = issue_result.get("key")
                issue_url = f"{jira_base_url.rstrip('/')}/browse/{issue_key}"
                
                return {
                    "success": True,
                    "action": "create_issue",
                    "data": {
                        "issue_key": issue_key,
                        "issue_id": issue_result.get("id"),
                        "issue_url": issue_url,
                        "project_key": project_key,
                        "issue_title": issue_title
                    },
                    "message": f"Issue '{issue_key}' created successfully!",
                    "url": issue_url
                }
            else:
                return {
                    "success": False,
                    "action": "create_issue",
                    "error": f"HTTP {response.status_code}",
                    "message": f"Failed to create issue. Status: {response.status_code}",
                    "response_text": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "action": "create_issue",
                "error": str(e),
                "message": "An unexpected error occurred while creating the issue."
            }
    
    # Action: Help/Guide
    elif action in ["help", "guide", "usage", "instructions"]:
        help_message = f"""
[JIRA] JIRA Project Manager Tool - Usage Guide

Available Actions:
1. 'list_projects' - Show all available JIRA projects
2. 'get_project' - Get details for a specific project by name/key
3. 'create_issue' - Create a new issue in a specified project
4. 'help' - Show this usage guide

[EXAMPLES] Examples:

# List all projects
JiraProjectManagerTool(action="list_projects")

# Get specific project details
JiraProjectManagerTool(
    action="get_project",
    project_name="My Project",
    project_key="MP"
)

# Create a simple issue
JiraProjectManagerTool(
    action="create_issue",
    project_key="MP",
    issue_title="Fix login bug",
    issue_description="Users cannot log in due to authentication error",
    issue_type="Bug",
    priority="High"
)

# Create a task with assignee
JiraProjectManagerTool(
    action="create_issue",
    project_key="DEV",
    issue_title="Implement new feature",
    issue_description="Add user profile management functionality",
    issue_type="Task", 
    priority="Medium",
    assignee="user@example.com"
)

[TIPS] Tips:
- Always check available projects first using action="list_projects"
- Project keys are usually short codes (e.g., "PROJ", "DEV", "TEST")
- Issue types include: Task, Bug, Story, Epic, Sub-task
- Priority levels: Highest, High, Medium, Low, Lowest
- Use email addresses for assignee parameter
        """
        
        return {
            "success": True,
            "action": "help",
            "data": {
                "available_actions": ["list_projects", "get_project", "create_issue", "help"],
                "examples_provided": True
            },
            "message": "Usage guide displayed. See console output for detailed instructions."
        }
    
    # Invalid action
    else:
        return {
            "success": False,
            "error": f"Invalid action: '{action}'",
            "message": "Valid actions are: 'list_projects', 'get_project', 'create_issue', 'help'",
            "usage": "JiraProjectManagerTool(action='help') for detailed usage instructions"
        }


if __name__ == "__main__":
    
    mcp.run(transport="stdio")
