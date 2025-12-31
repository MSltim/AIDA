# =============================================================================
# Vectorization Module - Document Processing and Embedding
# =============================================================================
# Provides document duplicate detection, chunking, embedding, and storage
# using Azure OpenAI embeddings and ChromaDB vector database.
# =============================================================================

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document

from utils.llm_connector import Model
from utils.logger import get_logger
from utils.input_file_handler import get_file_type_description

logger = get_logger(__name__)


# =============================================================================
# DocumentRegistry - Duplicate Detection and Document Tracking
# =============================================================================

class DocumentRegistry:
    """Tracks and detects duplicate documents using JSON registry."""
    
    def __init__(self, registry_file: str = None):
        """Initialize document registry"""
        if registry_file is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(current_dir)
            backend_dir = os.path.dirname(src_dir)
            registry_file = os.path.join(backend_dir, "storage", "resource", "document_registry.json")
        
        self.registry_file = registry_file
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from JSON file."""
        if not os.path.exists(self.registry_file):
            return {"documents": [], "last_updated": datetime.now().isoformat(), "total_documents": 0}
        
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load registry data: {e}")
            return {
                "documents": [],
                "last_updated": datetime.now().isoformat(),
                "total_documents": 0
            }
    
    def _save_registry(self, registry: Dict[str, Any]):
        """Save registry data to JSON file"""
        try:
            # Update timestamp
            registry["last_updated"] = datetime.now().isoformat()
            registry["total_documents"] = len(registry.get("documents", []))
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save registry data: {e}")
            raise
    
    def is_duplicate(self, filename: str, file_hash: str = None) -> bool:
        """Check if file already exists in registry by filename."""
        registry = self._load_registry()
        documents = registry.get("documents", [])
        
        # Check by filename
        for doc in documents:
            if doc.get("filename") == filename and doc.get("status") == "stored":
                logger.info(f"Found duplicate by filename: {filename}")
                return True
        
        return False
    
    def add_document(self, filename: str, file_path: str, file_type: str, 
                     chunks_count: int, persist_directory: str, 
                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a new document to the registry."""
        registry = self._load_registry()
        documents = registry.get("documents", [])
        next_id = max([d.get("id", 0) for d in documents], default=0) + 1
        
        doc_entry = {
            "id": next_id,
            "filename": filename,
            "file_path": file_path,
            "file_type": file_type,
            "status": "stored",
            "chunks_count": chunks_count,
            "vectorized_at": datetime.now().isoformat(),
            "persist_directory": persist_directory,
            "metadata": metadata or {}
        }
        
        documents.append(doc_entry)
        registry["documents"] = documents
        self._save_registry(registry)
        logger.info(f"Added document to registry: {filename} (ID: {next_id})")
        return doc_entry
    
    def update_document(self, filename: str, chunks_count: int, metadata: Dict[str, Any] = None):
        """Update an existing document in the registry."""
        registry = self._load_registry()
        for doc in registry.get("documents", []):
            if doc.get("filename") == filename:
                doc["chunks_count"] = chunks_count
                doc["vectorized_at"] = datetime.now().isoformat()
                if metadata:
                    doc["metadata"].update(metadata)
                break
        self._save_registry(registry)
        logger.info(f"Updated document in registry: {filename}")
    
    def get_document(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get a document entry by filename."""
        for doc in self._load_registry().get("documents", []):
            if doc.get("filename") == filename:
                return doc
        return None
    
    def list_all_documents(self) -> List[Dict[str, Any]]:
        """Get all stored documents from registry."""
        return self._load_registry().get("documents", [])

# =============================================================================
# Document Embedding and Vectorization
# =============================================================================

def DocumentEmbeddingIngestion(extracted_files: Dict[str, str], chunk_size: int = 1000, 
                               chunk_overlap: int = 100, registry_file: str = None) -> Dict[str, Any]:
    """Process files: chunk, embed, and store vectors in ChromaDB."""
    try:
        registry = DocumentRegistry(registry_file)
        documents = []
        file_metadata = {}
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        persist_directory = os.path.join(os.path.dirname(current_dir), "chroma_db")
        os.makedirs(persist_directory, exist_ok=True)
        
        for filename, content in extracted_files.items():
            if not content:
                logger.warning(f"Skipping empty content for file: {filename}")
                continue
            
            if registry.is_duplicate(filename):
                logger.info(f"Skipping duplicate file: {filename}")
                continue
            
            suffix = os.path.splitext(filename)[1].lower()
            file_type = get_file_type_description(suffix)
            
            doc = Document(
                page_content=content,
                metadata={
                    'filename': filename,
                    'file_type': file_type,
                    'processed_at': datetime.now().isoformat()
                }
            )
            documents.append(doc)
            file_metadata[filename] = {
                'file_path': os.path.join(persist_directory, filename),
                'file_type': file_type.lower().replace(' file', ''),
                'persist_directory': persist_directory
            }
            logger.info(f"Created document for {filename}")
        
        if not documents:
            logger.warning("No documents created or all files are duplicates")
            return {"status": "error", "chunks_stored": 0, "error": "No documents created", "registry_file": registry.registry_file}
        
        has_code_files = any(f.lower().endswith(('.py', '.sql', '.java', '.cpp', '.js', '.ts')) 
                            for f in [d.metadata.get('filename', '') for d in documents])
        adaptive_chunk_size = max(chunk_size, 2000) if has_code_files else chunk_size
        adaptive_overlap = max(chunk_overlap, 200) if has_code_files else chunk_overlap
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=adaptive_chunk_size,
            chunk_overlap=adaptive_overlap
        )
        split_docs = text_splitter.split_documents(documents)
        
        if not split_docs:
            return {"status": "error", "chunks_stored": 0, "error": "No chunks created"}
        
        chunks_per_file = {}
        for i, chunk in enumerate(split_docs):
            if not chunk.metadata:
                chunk.metadata = {}
            filename = chunk.metadata.get('filename', 'unknown')
            chunks_per_file[filename] = chunks_per_file.get(filename, 0) + 1
            chunk.metadata.update({
                'global_chunk_index': i,
                'file_chunk_index': chunks_per_file[filename] - 1,
                'total_chunks': len(split_docs),
                'chunk_size': len(chunk.page_content),
                'chunk_created_at': datetime.now().isoformat()
            })
        
        model_instance = Model()
        embedding_function = model_instance.get_embedding("azure", model_name="text-embedding-ada-002")
        logger.info(f"Storing {len(split_docs)} chunks in ChromaDB")
        
        if embedding_function is None:
            raise ValueError("Failed to initialize embedding function for vectorization")
        
        # Create vectorstore and explicitly persist
        vectorstore = Chroma.from_documents(
            split_docs,
            embedding=embedding_function,
            persist_directory=persist_directory,
            collection_name="langchain"
        )
        logger.info(f"Vectorstore created with collection 'langchain'")
        
        # Explicitly persist if method exists
        if hasattr(vectorstore, 'persist'):
            vectorstore.persist()
            logger.info("ChromaDB vectorstore persisted to disk")
        else:
            logger.info("ChromaDB vectorstore created (persist not required with LangChain Chroma)")
        
        # Update registry with newly stored documents
        for filename, metadata in file_metadata.items():
            chunks_count = chunks_per_file.get(filename, 0)
            registry.add_document(
                filename=filename,
                file_path=metadata['file_path'],
                file_type=metadata['file_type'],
                chunks_count=chunks_count,
                persist_directory=persist_directory,
                metadata={'processed_at': datetime.now().isoformat()}
            )
        
        files_processed = len(extracted_files)
        
        return {
            "status": "success",
            "chunks_stored": len(split_docs),
            "documents_processed": files_processed,
            "total_documents_loaded": len(documents),
            "message": f"Processed {files_processed} files, stored {len(split_docs)} chunks",
            "persist_directory": persist_directory,
            "registry_file": registry.registry_file
        }
        
    except Exception as e:
        logger.error(f"Error in DocumentEmbeddingIngestion: {e}")
        return {
            "status": "error",
            "chunks_stored": 0,
            "error": str(e),
            "error_type": type(e).__name__
        }