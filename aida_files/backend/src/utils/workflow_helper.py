"""AIDA Workflow Helper - Query processing and routing."""

import os
from typing import Dict, List, Optional, Any
from langchain_core.messages import HumanMessage
from utils.logger import get_logger

logger = get_logger(__name__)

# Optional evaluation tracking (disabled by default to not disturb existing code)
_eval_extractor = None
_eval_session_id = None
_enable_eval_tracking = False


def enable_evaluation_tracking(session_id: str = None, eval_path: str = None):
    """Enable trajectory evaluation tracking."""
    global _eval_extractor, _eval_session_id, _enable_eval_tracking
    
    try:
        from evaluations.run_eval import TrajectoryExtractor
        _eval_extractor = TrajectoryExtractor(eval_path)
        _eval_session_id = session_id
        _enable_eval_tracking = True
        logger.info(f"Evaluation tracking enabled (session_id={session_id})")
    except ImportError:
        logger.warning("Could not import TrajectoryExtractor. Evaluation tracking disabled.")
        _enable_eval_tracking = False


def disable_evaluation_tracking():
    """Disable trajectory evaluation tracking."""
    global _enable_eval_tracking
    _enable_eval_tracking = False
    logger.info("Evaluation tracking disabled")


def detect_rag_mode(user_input: str) -> bool:
    """Detect if RAG mode should be active (@doc or @rag tag)."""
    query_lower = user_input.lower()
    for tag in ['@doc', '@rag']:
        if tag in query_lower:
            logger.info(f"[RAG Detection] RAG mode ACTIVE: Found '{tag}' tag in query")
            return True
    logger.debug("[RAG Detection] RAG mode OFF: No @doc or @rag tag found")
    return False


def strip_rag_tags(user_input: str) -> str:
    """Remove @doc and @rag tags from user input."""
    import re
    cleaned = re.sub(r'@(doc|rag)\b', '', user_input, flags=re.IGNORECASE)
    return ' '.join(cleaned.split()).strip()



def is_file_query(user_input: str) -> bool:
    """Detect if query is asking about or referencing a file."""
    file_keywords = ['explain', 'show', 'analyze', 'what is', 'describe', 'review',
                     'summarize', 'breakdown', 'help', 'code', 'query', 'script',
                     'file', 'document', 'sql', 'python', 'sql file', 'py file']
    exclusion_keywords = ['date', 'time', 'today', 'tomorrow', 'yesterday', 'current',
                         'what time', 'what is the date', 'what is the time', 'when is',
                         'now', 'today\'s date', 'current date', 'current time']
    
    query_lower = user_input.lower()
    has_exclusion = any(keyword in query_lower for keyword in exclusion_keywords)
    if has_exclusion:
        return False
    return any(keyword in query_lower for keyword in file_keywords)


def should_route_to_rag_first(user_input: str, rag_mode_active: bool, has_chat_attachments: bool) -> bool:
    """Determine if query should route to RAGAgent first."""
    should_use_rag = rag_mode_active and is_file_query(user_input) and not has_chat_attachments
    logger.info(f"RAG-first routing decision: {should_use_rag} (RAG mode: {rag_mode_active}, "
                f"File query: {is_file_query(user_input)}, Chat attachments: {has_chat_attachments})")
    return should_use_rag


def _get_message_content(msg: Any) -> str:
    """Extract content from message, handling various formats."""
    content = getattr(msg, 'content', '')
    if isinstance(content, list):
        return ' '.join(str(item) for item in content)
    return str(content) if not isinstance(content, str) else content


def _extract_routing_path(all_messages: List[Any]) -> List[str]:
    """Extract routing path from message names."""
    routing_path = []
    current_query_start = 0
    
    for i in range(len(all_messages) - 1, -1, -1):
        if type(all_messages[i]).__name__ == 'HumanMessage':
            current_query_start = i + 1
            break
    
    for msg in all_messages[current_query_start:]:
        msg_name = getattr(msg, 'name', None)
        if msg_name in ['supervisor', 'ToolAgent', 'RAGAgent', 'ProjectManagementAgent', 'DeveloperAgent']:
            if msg_name not in routing_path:
                routing_path.append(msg_name)
    
    return routing_path


def _extract_agent_response(all_messages: List[Any]) -> tuple:
    """Extract agent response and responding agent from messages."""
    # First pass: Look for agent responses (excluding transfer messages)
    for msg in reversed(all_messages):
        msg_name = getattr(msg, 'name', None)
        if msg_name in ['ToolAgent', 'RAGAgent', 'ProjectManagementAgent', 'DeveloperAgent']:
            msg_content = _get_message_content(msg)
            if msg_content and 'Transferring back' not in msg_content and 'routing' not in msg_content.lower():
                # Log RAG responses for debugging
                if msg_name == 'RAGAgent' and msg_content:
                    logger.debug(f"RAG Agent response (first 200 chars): {msg_content[:200]}")
                return msg_content, msg_name
    
    # Second pass: Look for supervisor responses (excluding routing/transfer messages)
    for msg in reversed(all_messages):
        msg_name = getattr(msg, 'name', None)
        msg_content = _get_message_content(msg)
        if msg_name == 'supervisor' and msg_content and 'routing' not in msg_content.lower() and 'transfer' not in msg_content.lower():
            return msg_content, 'supervisor'
    
    # Fallback: Return last message
    if all_messages:
        final_message = all_messages[-1]
        return _get_message_content(final_message), getattr(final_message, 'name', 'unknown')
    
    return "No response generated", "unknown"


def _extract_tools_used(all_messages: List[Any]) -> List[str]:
    """Extract tools used from messages."""
    tracked_tools = []
    
    for msg in all_messages:
        msg_type = type(msg).__name__
        if msg_type == 'AIMessage':
            tool_calls = getattr(msg, 'tool_calls', [])
            for tool_call in tool_calls:
                tool_name = tool_call.get('name') if isinstance(tool_call, dict) else getattr(tool_call, 'name', None)
                if tool_name and tool_name not in tracked_tools and not tool_name.startswith('transfer_'):
                    tracked_tools.append(tool_name)
        elif msg_type == 'ToolMessage':
            tool_name = getattr(msg, 'name', None)
            if tool_name and tool_name not in tracked_tools and not tool_name.startswith('transfer_'):
                tracked_tools.append(tool_name)
    
    return tracked_tools


async def process_query(
    app,
    user_input: str,
    config: dict,
    attachments: Optional[List[Dict[str, Any]]] = None,
    debug: bool = False
) -> Dict:
    """
    Process a user query through the AIDA workflow and return structured response.
    
    Args:
        app: The compiled AIDA workflow
        user_input: User's query string
        config: Configuration dict with thread_id
        attachments: Optional list of attachment dicts with 'filename' and 'content' keys
        debug: Whether to print debug trace
    
    Returns:
        dict: {
            'final_message': str,
            'metadata': {
                'routing_path': list,
                'handled_by': str,
                'tools_used': list,
                'attachment_info': dict (if attachments were included)
            }
        }
    """
    try:
        # Detect RAG mode based on @doc or @rag tags in user input
        rag_mode_active = detect_rag_mode(user_input)
        has_chat_attachments = attachments and len(attachments) > 0
        
        # Strip @doc/@rag tags from the query for processing
        clean_user_input = strip_rag_tags(user_input) if rag_mode_active else user_input
        
        # Determine if query should route to RAG first
        route_to_rag_first = should_route_to_rag_first(
            clean_user_input,
            rag_mode_active,
            has_chat_attachments
        )
        
        # Attachments are processed via /api/upload endpoint
        # They are vectorized and stored in Chroma DB for RAG retrieval
        # No inline attachment processing needed here
        attachment_info = None
        
        logger.debug("Processing query - attachments handled via /api/upload endpoint")
        
        # Build enhanced input with context indicators for supervisor
        enhanced_input = clean_user_input
        
        # Add RAG mode indicator if @doc or @rag tag was used
        # This tells the supervisor to route to RAGAgent for document queries
        if rag_mode_active:
            enhanced_input = (
                f"[SYSTEM: RAG_MODE_ACTIVE - User requested document search with @doc/@rag tag]\n\n"
                f"{clean_user_input}"
            )
            logger.info("RAG mode active: User used @doc or @rag tag, routing through RAGAgent")
        
        result = await app.ainvoke(
            {"messages": [HumanMessage(content=enhanced_input)]},
            config=config
        )
        
        all_messages = result.get("messages", [])
        
        if debug:
            print("\n--- DEBUG: Workflow execution trace ---")
            for i, msg in enumerate(all_messages):
                msg_type = type(msg).__name__
                msg_name = getattr(msg, 'name', 'N/A')
                msg_content = getattr(msg, 'content', '')
                tool_calls = getattr(msg, 'tool_calls', None)
                print(f"Message {i}: Type={msg_type}, Name={msg_name}")
                if msg_content:
                    print(f"  Content: {msg_content[:200]}...")
                if tool_calls:
                    print(f"  Tool Calls: {tool_calls}")
            print("--- END DEBUG ---\n")
        
        routing_path = _extract_routing_path(all_messages)
        agent_response, responding_agent = _extract_agent_response(all_messages)
        tracked_tools = _extract_tools_used(all_messages)
        
        response_dict = {
            'final_message': agent_response,
            'metadata': {
                'routing_path': routing_path,
                'handled_by': responding_agent,
                'tools_used': tracked_tools
            }
        }
        
        if attachment_info:
            response_dict['metadata']['attachment_info'] = attachment_info
        
        if _enable_eval_tracking and _eval_extractor:
            try:
                user_query_lower = user_input.strip().lower()
                if user_query_lower not in ['hi', 'hello', 'hey', 'greetings']:
                    _eval_extractor.save_strategy1_response(
                        user_query=user_input,
                        output=agent_response,
                        session_id=_eval_session_id
                    )
                    _eval_extractor.save_strategy2_response(
                        user_query=user_input,
                        messages=all_messages,
                        agent_tools_used=tracked_tools if tracked_tools else None,
                        agent_output=agent_response,
                        final_response=agent_response,
                        session_id=_eval_session_id
                    )
            except Exception as eval_error:
                logger.warning(f"Error saving evaluation data: {eval_error}")
        
        return response_dict
        
    except Exception as e:
        logger.error(f"Error in process_query: {e}")
        return {
            'final_message': f"Error during agent invocation: {e}",
            'metadata': {
                'routing_path': [],
                'handled_by': 'error'
            }
        }
