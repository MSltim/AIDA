import os
import sys
from typing import List, Any
import asyncio

# Set up system path for relative imports
try:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
except NameError:
    sys.path.append(os.path.abspath('.'))

from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph_supervisor import create_supervisor

from utils.llm_connector import Model
from utils.logger import get_logger
from utils.workflow_helper import process_query

# Import tools loader from mcp_client
from tools.mcp_client import load_all_tools

# Import sub-agents from their respective folders
from agents.sub_agent.RagAgent.agent import RAGAgent
from agents.sub_agent.ProductOwner.agent import ProjectManagementAgent
from agents.sub_agent.Developer.agent import DeveloperAgent

# Import supervisor prompt
from agents.supervisor.prompt import SUPERVISOR_AGENT_PROMPT

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = get_logger(__name__)


async def setup_aida_workflow(provider: str = "azure", model: str = "gpt-4o", temperature: float = 0.3) -> CompiledStateGraph:
    """
    Initializes the AIDA workflow with all agents.
    All agents have access to all tools. Supervisor routes based on task type and @commands.
    Each agent is responsible for using only appropriate tools for their domain.
    
    Args:
        provider: The LLM provider (e.g., "azure", "openai")
        model: The model name (e.g., "gpt-4o")
        temperature: The temperature setting for the model
    
    Returns:
        Compiled workflow app.
    """
    logger.info("Initializing AIDA workflow with consistent agent routing...")
    
    # Ensure we have a proper event loop context
    try:
        loop = asyncio.get_running_loop()
        logger.info(f"Running in event loop: {loop}")
    except RuntimeError:
        logger.warning("No running event loop detected")
    
    # Use provided parameters for model configuration
    logger.info(f"Initializing workflow with: {provider} | {model} | temperature={temperature}")
    
    # Load all tools from mcp_client using load_all_tools
    # All agents get all tools; prompts ensure they use appropriate tools for their domain
    logger.info("Loading all MCP tools...")
    start_time = asyncio.get_event_loop().time()
    
    all_tools = await load_all_tools()
    
    end_time = asyncio.get_event_loop().time()
    loading_time = end_time - start_time
    logger.info(f"All tools loaded in {loading_time:.2f} seconds - Found {len(all_tools)} tools")
    
    # Initialize all agents with the same set of tools
    # Each agent's prompt ensures it uses only domain-appropriate tools
    logger.info("Initializing agents with consistent tool access...")
    
    developer_agent = await DeveloperAgent(
        provider=provider, 
        model_name=model, 
        temperature=temperature,
        tools=all_tools
    )
    logger.info("✓ DeveloperAgent initialized (code, SQL, API, database design)")
    
    product_owner_agent = await ProjectManagementAgent(
        provider=provider, 
        model_name=model, 
        temperature=temperature,
        tools=all_tools
    )
    logger.info("✓ ProjectManagementAgent initialized (user stories, sprints, planning, tasks)")
    
    rag_agent = await RAGAgent(
        provider=provider, 
        model_name=model, 
        temperature=temperature,
        tools=all_tools
    )
    logger.info("✓ RAGAgent initialized (document search, retrieval, analysis)")

    supervisor_llm = Model().get_llm(provider=provider, model_name=model, temperature=temperature)
    
    # All agents are included in the workflow
    # Supervisor routes based on @rag/@doc command for RAG or intelligent query analysis for others
    agents = [rag_agent, product_owner_agent, developer_agent]
    
    # Use centralized supervisor prompt
    supervisor_prompt = SUPERVISOR_AGENT_PROMPT
    logger.info("Supervisor configured for intelligent routing")
    logger.info("  - @rag/@doc commands → RAGAgent (document search, retrieval)")
    logger.info("  - Technical queries → DeveloperAgent (code, SQL, API, database)")
    logger.info("  - Project queries → ProjectManagementAgent (user stories, planning, tasks)")
    logger.info("  - General chat → ProjectManagementAgent")
    
    aida_workflow = create_supervisor(
        agents=agents,
        model=supervisor_llm,
        prompt=supervisor_prompt
    )

    app = aida_workflow.compile(checkpointer=MemorySaver())
    logger.info("AIDA Supervisor Workflow compiled successfully.")
    
    return app


async def main():
    """Main asynchronous loop for terminal interaction."""
    
    print("AIDA Supervisor Workflow Terminal Interface")
    print("Type your query and press Enter. Type 'exit' to quit.")

    app = None
    config = {"configurable": {"thread_id": "user-terminal-session-1"}}

    try:
        # The setup function returns the compiled app
        app = await setup_aida_workflow()
        
        # Warm up the workflow with a default "hi" message to avoid first-query issues
        print("Initializing conversation...")
        warmup_response = await process_query(app, "hi", config, debug=False)
        logger.info("Workflow warmed up successfully")

    except Exception as e:
        print(f"FATAL ERROR during workflow setup: {e}")
        return

    try:
        while True:
            try:
                user_input = input("User: ")
            except EOFError:
                print("\nExiting...")
                break
                
            if user_input.strip().lower() == "exit":
                print("Exiting...")
                break
            
            if not app:
                print("Workflow is not available due to a setup error.")
                continue

            # Add debugging logs to trace query routing
            print("Supervisor received query:", user_input)
            
            # Detect @rag/@doc commands for RAGAgent
            query_lower = user_input.lower()
            if '@rag' in query_lower or '@doc' in query_lower:
                print("[COMMAND DETECTED] @rag/@doc → Routing to RAGAgent")
            else:
                print("[ROUTING] Analyzing query to determine best agent...")

            # Process query and get structured response
            response = await process_query(app, user_input, config, debug=False)
            
            # Display metadata
            metadata = response['metadata']
            if metadata['routing_path']:
                path_display = " -> ".join(metadata['routing_path'])
                print(f"[ROUTING] Routing: {path_display}")
                print(f"[OK] Handled by: {metadata['handled_by']}\n")
            
            # Display final message
            print(f"AIDA: {response['final_message']}\n")

    finally:
        # Cleanup MCP client connections
        print("Cleaning up MCP connections...")
        # The mcp_client will be cleaned up when the process exits


if __name__ == "__main__":
    asyncio.run(main())
