import os
import sys
from typing import List, Any

# Set up system path for relative imports
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
except NameError:
    sys.path.append(os.path.abspath('.'))

from langgraph.prebuilt import create_react_agent

from utils.llm_connector import Model
from utils.logger import get_logger
from agents.sub_agent.ProductOwner.prompt import PROJECT_MANAGEMENT_AGENT_PROMPT

logger = get_logger(__name__)


async def ProjectManagementAgent(provider: str, model_name: str, temperature: float, tools: List[Any] = None) -> Any:
    """
    Initializes the Project Management agent with pre-loaded tools.
    
    This agent handles:
    - Project planning and task management
    - Team coordination and collaboration
    - Risk management
    - Trello and Jira integration for board management
    - Task creation and tracking
    - User stories and sprint planning
    
    Args:
        provider: The LLM provider (e.g., "azure", "openai")
        model_name: The model name (e.g., "gpt-4o")
        temperature: The temperature setting for the model
        tools: List of tools available to the agent
        
    Returns:
        Configured ProjectManagementAgent instance
    """
    if tools is None:
        tools = []
    
    logger.info(f"ProjectManagementAgent initialized with {len(tools)} tools.")
    
    agent = create_react_agent(
        name="ProjectManagementAgent",
        model=Model().get_llm(provider=provider, model_name=model_name, temperature=temperature),
        tools=tools,
        prompt=PROJECT_MANAGEMENT_AGENT_PROMPT
    )
    return agent
