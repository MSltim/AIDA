import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path


class TrajectoryExtractor:
    """
    Extracts supervisor agent trajectories and converts to evaluation formats.
    Supports two strategies:
    - Strategy 1 (IO_EVAL): Simple input-output pairs with tool tracking
    - Strategy 2 (TRAJECTORY): Complete execution traces with intermediate steps and tool usage
    
    Tool Tracking:
    Captures which tools each agent actually used during execution via the AgentWrapper mechanism.
    Tools are retrieved from app.__aida_wrapped_agents__[agent_name].__captured_tools__
    """

    def __init__(self, base_eval_path: str = None):
        """
        Initialize the trajectory extractor.
        
        Args:
            base_eval_path: Base path for evaluation storage. Defaults to script directory + evaluations
        """
        if base_eval_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_eval_path = os.path.join(script_dir, "chat_responses")
        
        self.base_path = base_eval_path
        self.strategy1_path = os.path.join(base_eval_path, "strategy1_io_eval")
        self.strategy2_path = os.path.join(base_eval_path, "strategy2_trajectory")
        
        # Create directories if they don't exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories for storing evaluation results."""
        os.makedirs(self.strategy1_path, exist_ok=True)
        os.makedirs(self.strategy2_path, exist_ok=True)
    
    def extract_tools_from_app(self, app: Any, responding_agent: str) -> List[str]:
        """
        Extract tools used by an agent from the app's wrapped agents.
        
        This retrieves tools captured during agent execution via the AgentWrapper mechanism.
        Each wrapped agent stores the tools it used in __captured_tools__.
        
        Args:
            app: The compiled AIDA workflow app
            responding_agent: Name of the agent that handled the query
        
        Returns:
            List of tool names used by the agent
        """
        try:
            # Get wrapped agents from the app object
            if hasattr(app, '__aida_wrapped_agents__'):
                wrapped_agents = app.__aida_wrapped_agents__
                
                # Get the wrapped agent for the responding agent
                if responding_agent in wrapped_agents:
                    wrapped_agent = wrapped_agents[responding_agent]
                    
                    # Get captured tools from the agent's __captured_tools__ attribute
                    if hasattr(wrapped_agent, '__captured_tools__'):
                        return wrapped_agent.__captured_tools__
        except Exception as e:
            # Silently fail - tool tracking is optional
            pass
        
        return []

    def extract_intermediate_steps(self, messages: List[Any], user_query: str = None,
                                   agent_tools_used: List[str] = None, 
                                   agent_output: str = None) -> Tuple[List[Dict], str, str]:
        """
        Extract intermediate steps from supervisor messages showing all agents that handled the query.
        
        Creates a list of agent entries, each containing:
        - agent_name: {
            "input": user query passed to agent,
            "tool_used": list of tools used (only for final agent),
            "output": agent's output
          }
        
        Includes ALL agents in the routing path.
        
        Args:
            messages: List of messages from supervisor execution
            user_query: The original user query (optional, will be extracted from messages if not provided)
            agent_tools_used: List of tools used by the final agent (optional override, only applied to final agent)
            agent_output: Final output from the agent (optional override)
        
        Returns:
            Tuple of (formatted_intermediate_steps_list, final_agent, agent_query)
        """
        # If user_query not provided, extract from messages
        if not user_query:
            for message in messages:
                msg_name = getattr(message, 'name', None)
                msg_content = getattr(message, 'content', '')
                # HumanMessage: has content, no name, and isn't empty
                if msg_name is None and msg_content and len(msg_content.strip()) > 0:
                    user_query = msg_content
                    break
        
        # Filter out transfer tools - keep only real tools
        final_agent_tools = []
        if agent_tools_used:
            for tool in agent_tools_used:
                if not tool.startswith('transfer_'):
                    final_agent_tools.append(tool)
        
        # Collect ALL non-supervisor agents with their outputs
        # Track unique agents in order of appearance to avoid duplicates
        agent_steps = {}  # {agent_name: {"input": ..., "output": ..., "order": position}}
        final_agent = None
        
        for i, message in enumerate(messages):
            msg_name = getattr(message, 'name', None)
            content = getattr(message, 'content', '')
            msg_type = type(message).__name__
            
            # Skip supervisor and transfer messages
            if msg_name is None or msg_name == 'supervisor':
                continue
            
            # Skip transfer confirmation messages
            if 'Transferring' in content or 'transfer' in content.lower():
                continue
            
            # Skip empty responses
            if not content or len(content.strip()) == 0:
                continue
            
            # This is a real agent response
            if msg_name not in agent_steps:
                agent_steps[msg_name] = {
                    "input": user_query or "",
                    "output": content,
                    "order": i,
                    "tool_used": []  # Will be populated for final agent
                }
            else:
                # Update with latest output from this agent
                agent_steps[msg_name]["output"] = content
                agent_steps[msg_name]["order"] = i
            
            final_agent = msg_name
        
        # Build the result with all agents in order
        formatted_intermediate_steps = []
        sorted_agents = sorted(agent_steps.items(), key=lambda x: x[1]["order"])
        
        for agent_name, agent_info in sorted_agents:
            # Only add tools to the final agent
            if agent_name == final_agent and agent_tools_used:
                agent_info["tool_used"] = final_agent_tools
            else:
                agent_info["tool_used"] = []
            
            step = {
                agent_name: {
                    "input": agent_info["input"],
                    "tool_used": agent_info["tool_used"],
                    "output": agent_info["output"]
                }
            }
            formatted_intermediate_steps.append(step)
        
        return formatted_intermediate_steps, final_agent, user_query

    def create_trajectory_response(self, user_query: str, messages: List[Any], 
                                   agent_tools_used: List[str] = None, 
                                   agent_output: str = None, 
                                   final_response: str = None) -> Dict[str, Any]:
        """
        Create a complete trajectory response structure for Strategy 2.
        
        Args:
            user_query: Original user query
            messages: List of all messages from supervisor execution
            agent_tools_used: Tools used by the routed agent
            agent_output: Output from the routed agent
            final_response: Final response to user
        
        Returns:
            Dictionary with supervisor_agent trajectory structure
        """
        formatted_intermediate_steps, _, _ = self.extract_intermediate_steps(
            messages,
            user_query=user_query,
            agent_tools_used=agent_tools_used if agent_tools_used else None,
            agent_output=agent_output
        )
        
        return {
            "supervisor_agent": {
                "input": user_query,
                "intermediate_steps": formatted_intermediate_steps,
                "output": final_response or "No response"
            }
        }

    def save_strategy1_response(self, user_query: str, output: str, 
                               app: Any = None, responding_agent: str = None,
                               session_id: str = None) -> str:
        """
        Save response to Strategy 1 (IO_EVAL) format.
        Creates a dataframe with columns: timestamp, user_query, output
        
        Simple input-output pairs with timestamp.
        
        Args:
            user_query: User's input query
            output: Agent's output response
            app: Compiled workflow app (optional, not used in strategy 1)
            responding_agent: Name of agent that handled the query (optional, not used in strategy 1)
            session_id: Optional session identifier (not used in strategy 1)
        
        Returns:
            Path to saved CSV file
        """
        timestamp = datetime.now().isoformat()
        
        data = {
            "timestamp": [timestamp],
            "user_query": [user_query],
            "output": [output]
        }
        
        df = pd.DataFrame(data)
        
        # Load existing data if file exists and append
        csv_file = os.path.join(self.strategy1_path, "io.csv")
        if os.path.exists(csv_file):
            existing_df = pd.read_csv(csv_file)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_csv(csv_file, index=False)
        return csv_file

    def save_strategy2_response(self, user_query: str, messages: List[Any], 
                               app: Any = None,
                               agent_tools_used: List[str] = None,
                               agent_output: str = None,
                               final_response: str = None,
                               responding_agent: str = None,
                               session_id: str = None) -> str:
        """
        Save response to Strategy 2 (TRAJECTORY) format.
        Creates a dataframe with columns: timestamp, user_query, trajectory_json, output
        where trajectory_json contains the complete trajectory with intermediate steps.
        
        Args:
            user_query: User's input query
            messages: All messages from supervisor execution
            app: Compiled workflow app (optional, used to extract tools)
            agent_tools_used: Tools used by routed agent (optional override)
            agent_output: Output from routed agent
            final_response: Final response to user
            responding_agent: Name of agent that handled the query
            session_id: Optional session identifier (not used in this version)
        
        Returns:
            Path to saved CSV file
        """
        # Extract tools if not provided
        if agent_tools_used is None and app and responding_agent:
            agent_tools_used = self.extract_tools_from_app(app, responding_agent)
        
        # Create trajectory response with actual tools
        trajectory_response = self.create_trajectory_response(
            user_query, messages, agent_tools_used, agent_output, final_response
        )
        
        # Prepare data for strategy 2
        timestamp = datetime.now().isoformat()
        
        data = {
            "timestamp": [timestamp],
            "user_query": [user_query],
            "trajectory_json": [json.dumps(trajectory_response, indent=2)],
            "output": [final_response or "No response"]
        }
        
        df = pd.DataFrame(data)
        
        # Load existing data if file exists and append
        csv_file = os.path.join(self.strategy2_path, "trajectory.csv")
        if os.path.exists(csv_file):
            existing_df = pd.read_csv(csv_file)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_csv(csv_file, index=False)
        return csv_file

    def get_strategy1_dataframe(self) -> pd.DataFrame:
        """
        Load Strategy 1 responses as a DataFrame.
        
        Returns:
            DataFrame with columns: timestamp, user_query, output
        """
        csv_file = os.path.join(self.strategy1_path, "io.csv")
        if os.path.exists(csv_file):
            return pd.read_csv(csv_file)
        else:
            return pd.DataFrame(columns=["timestamp", "user_query", "output"])

    def get_strategy2_dataframe(self) -> pd.DataFrame:
        """
        Load Strategy 2 responses as a DataFrame.
        
        Returns:
            DataFrame with columns: timestamp, user_query, trajectory_json, output
        """
        csv_file = os.path.join(self.strategy2_path, "trajectory.csv")
        if os.path.exists(csv_file):
            return pd.read_csv(csv_file)
        else:
            return pd.DataFrame(columns=["timestamp", "user_query", "trajectory_json", "output"])

    def print_strategy_stats(self):
        """Print statistics about saved responses for both strategies."""
        df1 = self.get_strategy1_dataframe()
        df2 = self.get_strategy2_dataframe()
        
        print("\n" + "="*60)
        print("EVALUATION STATISTICS")
        print("="*60)
        print(f"Strategy 1 (IO_EVAL): {len(df1)} responses saved")
        print(f"Strategy 2 (TRAJECTORY): {len(df2)} responses saved")
        print(f"Strategy 1 Path: {self.strategy1_path}")
        print(f"Strategy 2 Path: {self.strategy2_path}")
        print("="*60 + "\n")
    
    async def save_evaluation_response(self, user_query: str, app: Any, 
                                      response_dict: Dict[str, Any],
                                      strategy: str = "both",
                                      session_id: str = None) -> Dict[str, str]:
        """
        Convenience method to save evaluation responses with tool tracking.
        
        Automatically extracts all necessary information from the response dictionary
        returned by process_query() and saves to both strategies.
        
        Args:
            user_query: Original user query
            app: Compiled workflow app
            response_dict: Response dictionary from process_query() containing:
                - final_message: str
                - messages: List of all messages
                - metadata: dict with routing_path, handled_by, tools_used
            strategy: Which strategy to save ("strategy1", "strategy2", or "both")
            session_id: Optional session identifier
        
        Returns:
            Dictionary with paths to saved files: {"strategy1": path1, "strategy2": path2}
        """
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        final_message = response_dict.get('final_message', '')
        all_messages = response_dict.get('messages', [])
        metadata = response_dict.get('metadata', {})
        
        handled_by = metadata.get('handled_by', 'unknown')
        tools_used = metadata.get('tools_used', [])
        
        # Extract tools from app if not in metadata
        if not tools_used and handled_by != 'unknown':
            tools_used = self.extract_tools_from_app(app, handled_by)
        
        saved_paths = {}
        
        if strategy in ["strategy1", "both"]:
            path = self.save_strategy1_response(
                user_query=user_query,
                output=final_message,
                app=app,
                responding_agent=handled_by,
                session_id=session_id
            )
            saved_paths["strategy1"] = path
            print(f"[OK] Saved to Strategy 1: {path}")
        
        if strategy in ["strategy2", "both"]:
            path = self.save_strategy2_response(
                user_query=user_query,
                messages=all_messages,
                app=app,
                agent_tools_used=tools_used,
                final_response=final_message,
                responding_agent=handled_by,
                session_id=session_id
            )
            saved_paths["strategy2"] = path
            print(f"[OK] Saved to Strategy 2: {path}")
        
        return saved_paths
