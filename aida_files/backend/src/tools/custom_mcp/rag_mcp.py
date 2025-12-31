import os
import sys
from typing import Dict, Any
import time

from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP

# Add parent directories to sys.path for imports
for path in [
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')),  # AIDA root
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')),  # backend/src root (where utils is)
]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import utilities
try:
    from utils.llm_connector import Model
except ImportError as e:
    print(f"Failed to import Model: {e}", file=sys.stderr)
    Model = None

# Import ChromaDB components
try:
    from langchain_chroma import Chroma
    CHROMA_AVAILABLE = True
except ImportError as e:
    print(f"ChromaDB import error: {e}", file=sys.stderr)
    CHROMA_AVAILABLE = False

# Load environment variables with multiple fallback paths
def load_env_variables():
    """Load .env from multiple possible locations"""
    env_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')),  # AIDA/.env
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'),  # relative
        find_dotenv(),  # automatic search
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print(f"Loading .env from: {env_path}", file=sys.stderr)
            load_dotenv(env_path, override=True)
            return env_path
    
    print(f"Warning: .env file not found in paths: {env_paths}", file=sys.stderr)
    load_dotenv(find_dotenv(), override=True)
    return None

load_env_variables()

mcp = FastMCP("RAG MCP Tools", "0.1.0")

@mcp.tool()
def CurrentDateTool() -> str:
    """
    Description: Current Date and Time Provider - Returns today's date and current timestamp for scheduling, planning, and time-based operations.
    Use this when you need to set due dates, create timestamps, schedule tasks, or perform any date-related calculations for project management.
    
    Arguments: None
    
    Returns: str - Today's date and current time formatted as 'DD-MMM-YYYY HH:MM:SS' (e.g., '29-Oct-2025 14:30:45').
    """
    return time.strftime("%d-%b-%Y %H:%M:%S")

@mcp.tool()
async def rag_document_search(query: str) -> str:
    """
    Search for relevant information in uploaded documents using RAG (Retrieval Augmented Generation).
    
    Args:
        query (str): The search query or question to find relevant information for
    
    Returns:
        str: Formatted search results as a readable string with document content and metadata
    """
    try:
        # Check if ChromaDB is available
        if not CHROMA_AVAILABLE:
            error_msg = "Error: ChromaDB is not available. Please install langchain-chroma package."
            print(error_msg, file=sys.stderr)
            return error_msg
        
        # Check if ChromaDB directory exists
        persist_directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_db')
        )
        
        if not os.path.exists(persist_directory):
            error_msg = f"Document database not found at {persist_directory}. Please upload documents first."
            print(f"Error: {error_msg}", file=sys.stderr)
            return error_msg
        
        # Initialize embeddings
        embedding_function = None
        
        try:
            # Check if environment variables are set
            api_key = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY")
            api_endpoint = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
            
            # Handle quoted values from .env file
            if api_key:
                api_key = api_key.strip("'\"")
            if api_endpoint:
                api_endpoint = api_endpoint.strip("'\"")
            
            if not api_key or not api_endpoint:
                error_msg = "Azure embedding credentials not configured in environment"
                print(f"Error: {error_msg}", file=sys.stderr)
                return error_msg
            
            if Model is None:
                error_msg = "Model class could not be imported"
                print(f"Error: {error_msg}", file=sys.stderr)
                return error_msg
            
            model_instance = Model()
            embedding_function = model_instance.get_embedding("azure", model_name="text-embedding-ada-002")
            
            if embedding_function is None:
                error_msg = "Failed to initialize embedding function - returned None"
                print(f"[RAG_MCP] Error: {error_msg}", file=sys.stderr)
                return error_msg
            
            print(f"[RAG_MCP] Embedding function initialized successfully", file=sys.stderr)
        except ValueError as e:
            error_msg = f"Configuration error: {str(e)}"
            print(f"[RAG_MCP] ValueError: {e}", file=sys.stderr)
            return error_msg
        except TimeoutError as e:
            error_msg = "Timeout initializing embeddings. Azure OpenAI service may be slow."
            print(f"[RAG_MCP] TimeoutError: {e}", file=sys.stderr)
            return error_msg
        except Exception as e:
            error_msg = f"Failed to initialize embeddings: {str(e)}"
            print(f"[RAG_MCP] Exception during embedding initialization: {e}", file=sys.stderr)
            import traceback
            print(f"[RAG_MCP] Traceback:", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            return error_msg
        
        if not embedding_function:
            error_msg = "Failed to initialize embeddings: embedding function is None"
            print(f"[RAG_MCP] Error: {error_msg}", file=sys.stderr)
            return error_msg
        
        # Load vector database
        try:
            print(f"[RAG_MCP] Loading Chroma vectorstore from: {persist_directory}", file=sys.stderr)
            # Load Chroma vectorstore with collection
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_function,
                collection_name="langchain"
            )
            print(f"[RAG_MCP] Vectorstore loaded successfully", file=sys.stderr)
            
        except Exception as e:
            error_msg = f"Failed to load vector database: {str(e)}"
            print(f"[RAG_MCP] Exception loading vectorstore: {e}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            return error_msg
        
        # Perform similarity search
        try:
            print(f"[RAG_MCP] Performing similarity search for query: {query[:100]}", file=sys.stderr)
            docs_and_scores = vectorstore.similarity_search_with_score(query, k=5)
            print(f"[RAG_MCP] Search returned {len(docs_and_scores)} results", file=sys.stderr)
            
            if not docs_and_scores:
                print(f"[RAG_MCP] Warning: No results found for query: {query}", file=sys.stderr)
                return f"No relevant documents found for the query: '{query}'"
            
            # Format results as readable text for the LLM
            formatted_response = f"Found {len(docs_and_scores)} relevant document(s) for '{query}':\n\n"
            
            for i, (doc, score) in enumerate(docs_and_scores, 1):
                metadata = doc.metadata if doc.metadata else {}
                source = metadata.get("source", "Unknown")
                filename = metadata.get("filename", "Unknown") 
                page = metadata.get("page", "N/A")
                
                formatted_response += f"Document {i} (Relevance: {score:.2%}):\n"
                formatted_response += f"  Source: {filename}\n"
                formatted_response += f"  Page: {page}\n"
                formatted_response += f"  Content: {doc.page_content[:500]}\n"
                if len(doc.page_content) > 500:
                    formatted_response += f"  ...[truncated, {len(doc.page_content)} chars total]\n"
                formatted_response += "\n"
            
            print(f"[RAG_MCP] Formatted response ready ({len(formatted_response)} chars)", file=sys.stderr)
            return formatted_response
            
        except Exception as e:
            error_msg = f"Error during document search: {str(e)}"
            print(f"[RAG_MCP] Exception during similarity search: {e}", file=sys.stderr)
            import traceback
            print(traceback.format_exc(), file=sys.stderr)
            return error_msg
            
    except Exception as e:
        error_msg = f"Unexpected error in RAG search: {str(e)}"
        print(f"[RAG_MCP] Unexpected exception: {error_msg}", file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)
        return error_msg


if __name__ == "__main__":
    mcp.run(transport="stdio")