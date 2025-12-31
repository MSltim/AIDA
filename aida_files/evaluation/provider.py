"""
Promptfoo Provider for AIDA Agent
This module provides the API interface for Promptfoo to evaluate the AIDA workflow.
"""

import sys
import os
import asyncio

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src')))

from dotenv import load_dotenv
load_dotenv()

from backend.src.agents.supervisor.agent import setup_aida_workflow
from backend.src.utils.workflow_helper import process_query

# Global workflow instance (cached for performance)
_aida_app = None
_config = {"configurable": {"thread_id": "promptfoo-eval-session"}}


async def get_aida_workflow():
    """Get or create the AIDA workflow instance."""
    global _aida_app
    if _aida_app is None:
        print("[INFO] Initializing AIDA workflow for evaluation...")
        _aida_app = await setup_aida_workflow(
            provider="azure",
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT_MODEL_NAME', 'gpt-4o'),
            temperature=0.3
        )
        print("[OK] AIDA workflow initialized successfully")
    return _aida_app


async def run_aida_agent(prompt: str) -> dict:
    """
    Run the AIDA agent with the given prompt.
    
    Args:
        prompt: The user query to process
        
    Returns:
        dict: Response containing the agent's output
    """
    def sanitize_ascii(text):
        if isinstance(text, str):
            return text.encode("ascii", "replace").decode("ascii")
        return text

    try:
        app = await get_aida_workflow()
        response = await process_query(app, prompt, _config, debug=False)
        # Sanitize all string fields in the response dict
        if isinstance(response, dict):
            response = {k: sanitize_ascii(v) for k, v in response.items()}
        elif isinstance(response, str):
            response = sanitize_ascii(response)
        return {
            "success": True,
            "query": sanitize_ascii(prompt),
            "response": response,
            "agent": "AIDA Supervisor"
        }
    except Exception as e:
        return {
            "success": False,
            "query": sanitize_ascii(prompt),
            "error": sanitize_ascii(str(e)),
            "agent": "AIDA Supervisor"
        }


def call_api(prompt: str, options: dict, context: dict) -> dict:
    """
    Main API function called by Promptfoo.
    
    Args:
        prompt: The evaluation prompt
        options: Additional options (unused)
        context: Contextual information (unused)
        
    Returns:
        dict: A dictionary containing the agent's output or an error message
    """
    import os
    # Ensure SESSION_ID is set for MCP tools
    if not os.environ.get("SESSION_ID"):
        os.environ["SESSION_ID"] = context.get("sessionId", "promptfoo-eval-session")
    try:
        # Run the async function in an event loop
        result = asyncio.run(run_aida_agent(prompt))
        return {"output": result}
    except Exception as e:
        return {"output": {"success": False, "error": f"Error: {str(e)}"}}


# Test the provider directly
if __name__ == "__main__":
    print("[OK] Testing AIDA Agent provider...")
    test_prompt = "What tools do you have available?"
    result = call_api(test_prompt, {}, {})
    print("Provider result:", result)
