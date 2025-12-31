import os
import sys
from typing import Optional, Dict, Any
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings

# Load environment variables once at module level
load_dotenv()

class Model:
    """
    A unified factory class for creating and managing both LLM and Embedding models
    from different providers (Google Gemini, OpenAI, Ollama).
    
    Features:
    - Centralized API key management
    - Model caching to avoid redundant initialization
    - Support for both chat models and embeddings
    - Comprehensive error handling
    """
    
    def __init__(self):
        """Initialize the factory by loading all API keys from environment variables."""
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_endpoint = os.getenv('AZURE_ENDPOINT')
        self.azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        self.azure_embedding_api_key = os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY')
        self.azure_embedding_api_endpoint = os.getenv('AZURE_OPENAI_EMBEDDING_ENDPOINT')

        # Cache for initialized models to avoid redundant initialization
        self._model_cache: Dict[str, Any] = {}
        self._embedding_cache: Dict[str, Any] = {}
    
    # ==================== LLM Methods ====================
    
    def get_llm(self, provider: str, model_name: str, temperature: float = 0.7, 
                use_cache: bool = True, **kwargs) -> Any:
        """
        Creates and returns an initialized LangChain LLM instance.

        Args:
            provider (str): The provider to use ('gemini', 'openai', or 'ollama').
            model_name (str): The specific model name.
            temperature (float): The temperature setting for the model (default: 0.7).
            use_cache (bool): Whether to use cached model if available (default: True).
            **kwargs: Additional provider-specific parameters.

        Returns:
            An initialized LangChain chat model instance.

        Raises:
            ValueError: If provider is unknown or API key is missing.
            RuntimeError: If model initialization fails.
        """
        cache_key = f"{provider}_{model_name}_{temperature}"
        
        # Return cached model if available and caching is enabled
        if use_cache and cache_key in self._model_cache:
            return self._model_cache[cache_key]
        
        provider_lower = provider.lower()
        
        if provider_lower == "google":
            model = self._initialize_gemini_llm(model_name, temperature, **kwargs)
        elif provider_lower == "azure":
            model = self._initialize_azure_llm(model_name, temperature, **kwargs)
        elif provider_lower == "ollama":
            model = self._initialize_ollama_llm(model_name, temperature, **kwargs)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}. Supported: gemini, openai, ollama")
        
        # Cache the model
        if use_cache:
            self._model_cache[cache_key] = model
        
        return model
    
    def _initialize_gemini_llm(self, model_name: str, temperature: float, **kwargs) -> ChatGoogleGenerativeAI:
        """Initialize and return a Gemini chat model instance."""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables.")
        
        try:
            return ChatGoogleGenerativeAI(
                api_key=self.google_api_key,
                model=model_name,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini LLM: {e}")
    
    def _initialize_azure_llm(self, model_name: str, temperature: float) -> AzureChatOpenAI:
        """Initializes and returns an Azure OpenAI model instance."""
        if not all([self.azure_api_key, self.azure_endpoint, self.azure_api_version]):
            raise ValueError("One or more Azure OpenAI environment variables are missing (API_KEY, ENDPOINT, API_VERSION).")
        
        try:
            azure_model = AzureChatOpenAI(
                azure_deployment=model_name, 
                openai_api_version=self.azure_api_version,
                azure_endpoint=self.azure_endpoint, 
                api_key=self.azure_api_key, 
                temperature=temperature
            )
            print(f"Successfully initialized LLM model: {model_name}")
            return azure_model
        except Exception as e:
            raise RuntimeError(f"Error initializing Azure model: {e}") from e
        
    def _initialize_ollama_llm(self, model_name: str, temperature: float, **kwargs) -> ChatOllama:
        """Initialize and return an Ollama chat model instance."""
        try:
            return ChatOllama(
                model=model_name,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Ollama LLM: {e}")
    
    # ==================== Embedding Methods ====================
    
    def get_embedding(self, provider: str, model_name: str = None, 
                     use_cache: bool = True, **kwargs) -> Any:
        """
        Creates and returns an initialized LangChain Embedding model instance.

        Args:
            provider (str): The provider to use ('gemini', 'openai', or 'ollama').
            model_name (str): The specific embedding model name (optional, uses defaults).
            use_cache (bool): Whether to use cached model if available (default: True).
            **kwargs: Additional provider-specific parameters.

        Returns:
            An initialized LangChain embedding model instance.

        Raises:
            ValueError: If provider is unknown or API key is missing.
            RuntimeError: If embedding model initialization fails.
        """
        cache_key = f"embedding_{provider}_{model_name}"
        
        # Return cached embedding model if available
        if use_cache and cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        provider_lower = provider.lower()
        
        if provider_lower == "gemini":
            embedding = self._initialize_gemini_embedding(model_name, **kwargs)
        elif provider_lower == "azure":
            embedding = self._initialize_openai_embedding(model_name, **kwargs)
        elif provider_lower == "ollama":
            embedding = self._initialize_ollama_embedding(model_name, **kwargs)
        else:
            raise ValueError(f"Unknown embedding provider: {provider}. Supported: gemini, openai, ollama")
        
        # Cache the embedding model
        if use_cache:
            self._embedding_cache[cache_key] = embedding
        
        return embedding

    def _initialize_gemini_embedding(self, model_name: Optional[str] = None, **kwargs) -> GoogleGenerativeAIEmbeddings:
        """Initialize and return a Gemini embedding model instance."""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables.")
        
        try:
            # Default Gemini embedding model
            model = model_name or "models/embedding-001"
            return GoogleGenerativeAIEmbeddings(
                google_api_key=self.google_api_key,
                model=model,
                **kwargs
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini embeddings: {e}")
    
    def _initialize_openai_embedding(self, model_name: Optional[str] = None, **kwargs) -> AzureOpenAIEmbeddings:
        """Initialize and return an OpenAI embedding model instance."""
        if not self.azure_embedding_api_key:
            raise ValueError("AZURE_OPENAI_EMBEDDING_API_KEY is not set in environment variables.")
        
        if not self.azure_embedding_api_endpoint:
            raise ValueError("AZURE_OPENAI_EMBEDDING_ENDPOINT is not set in environment variables.")
        
        try:
            # Default OpenAI embedding model - use text-embedding-ada-002 for Azure
            model = model_name or "text-embedding-ada-002"
            embedding = AzureOpenAIEmbeddings(
                model=model,
                api_key=self.azure_embedding_api_key,
                azure_endpoint=self.azure_embedding_api_endpoint,
                **kwargs
            )
            print(f"Successfully initialized Azure OpenAI Embeddings: {model}")
            return embedding
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure OpenAI embeddings: {e}")
    
    def _initialize_ollama_embedding(self, model_name: Optional[str] = None, **kwargs) -> OllamaEmbeddings:
        """Initialize and return an Ollama embedding model instance."""
        try:
            model = model_name or "nomic-embed-text"
            return OllamaEmbeddings(model=model, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Ollama embeddings: {e}")
    
    # ==================== Utility Methods ====================
    
    def clear_cache(self):
        """Clear all cached models and embeddings."""
        self._model_cache.clear()
        self._embedding_cache.clear()
    
    def get_available_providers(self) -> Dict[str, Dict[str, bool]]:
        """
        Returns information about which providers are available based on API keys.
        
        Returns:
            Dict containing availability status for each provider.
        """
        return {
            "llm": {
                "gemini": bool(self.google_api_key),
                "azure": bool(self.azure_api_key and self.azure_endpoint),
                "ollama": True  # Ollama doesn't require API key
            },
            "embedding": {
                "gemini": bool(self.google_api_key),
                "azure": bool(self.azure_embedding_api_key and self.azure_embedding_api_endpoint)
            }
        }

