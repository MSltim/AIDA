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
from agents.sub_agent.RagAgent.prompt import RAG_AGENT_PROMPT

logger = get_logger(__name__)


async def RAGAgent(provider: str, model_name: str, temperature: float, tools: List[Any] = None) -> Any:
    """
    Initializes the RAG agent with pre-loaded RAG retrieval tools.
    
    This agent handles:
    - Document searches using RAG
    - Research and document analysis
    - Information retrieval from vector stores
    - Citation and source tracking
    
    Args:
        provider: The LLM provider (e.g., "azure", "openai")
        model_name: The model name (e.g., "gpt-4o")
        temperature: The temperature setting for the model
        tools: List of tools available to the agent
        
    Returns:
        Configured RAGAgent instance
    """
    if tools is None:
        tools = []
    
    logger.info(f"RAGAgent initialized with {len(tools)} tools.")
    
    agent = create_react_agent(
        name="RAGAgent",
        model=Model().get_llm(provider=provider, model_name=model_name, temperature=temperature),
        tools=tools,
        prompt=RAG_AGENT_PROMPT
    )
    return agent
