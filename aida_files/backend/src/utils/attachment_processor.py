"""
Attachment Processor - Vectorization and Chroma DB Storage

Simple processor for handling file attachments:
1. Read file content
2. Vectorize using DocumentEmbeddingIngestion
3. Store in Chroma DB for RAG retrieval
4. RAG system retrieves relevant attachments when needed
"""

import os
import sys
import tempfile
from typing import List, Dict, Any, Optional

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.logger import get_logger
from utils.input_file_handler import get_document_loader
from utils.vectorization import DocumentEmbeddingIngestion

logger = get_logger(__name__)

# File size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file


def process_attachment(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    registry_file: str = None
) -> Dict[str, Any]:
    """
    Process a single attachment file: read, vectorize, and store in Chroma.
    
    Uses input_file_handler for loading and vectorization module for storage.
    
    Args:
        file_path: Path to the attachment file
        chunk_size: Size of text chunks (default: 1000)
        chunk_overlap: Overlap between chunks (default: 100)
        registry_file: Path to document registry file for duplicate detection
    
    Returns:
        Dict with:
            - 'success': bool
            - 'filename': str
            - 'chunks_stored': int
            - 'message': str
    """
    filename = os.path.basename(file_path)
    
    try:
        # Validate file exists and size
        if not os.path.exists(file_path):
            return {
                'success': False,
                'filename': filename,
                'chunks_stored': 0,
                'message': f"File not found: {file_path}"
            }
        
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return {
                'success': False,
                'filename': filename,
                'chunks_stored': 0,
                'message': f"File too large: {file_size / 1024 / 1024:.1f}MB (max {MAX_FILE_SIZE / 1024 / 1024:.0f}MB)"
            }
        
        logger.info(f"Processing attachment: {filename}")
        
        # Load file using input_file_handler
        loaders = get_document_loader([file_path])
        documents = loaders[0].load()
        
        if not documents:
            return {
                'success': False,
                'filename': filename,
                'chunks_stored': 0,
                'message': "No content extracted from file"
            }
        
        # Extract content from loaded documents
        content = '\n'.join([doc.page_content for doc in documents])
        
        # Vectorize and store using DocumentEmbeddingIngestion
        extracted_files = {filename: content}
        result = DocumentEmbeddingIngestion(
            extracted_files=extracted_files,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            registry_file=registry_file
        )
        
        if result.get('status') == 'success':
            logger.info(f"Successfully stored attachment in Chroma: {filename} ({result.get('chunks_stored', 0)} chunks)")
            return {
                'success': True,
                'filename': filename,
                'chunks_stored': result.get('chunks_stored', 0),
                'message': f"Stored {result.get('chunks_stored', 0)} chunks in Chroma"
            }
        else:
            return {
                'success': False,
                'filename': filename,
                'chunks_stored': 0,
                'message': result.get('error', 'Vectorization failed')
            }
    
    except Exception as e:
        logger.error(f"Error processing attachment {filename}: {e}")
        return {
            'success': False,
            'filename': filename,
            'chunks_stored': 0,
            'message': f"Error: {str(e)}"
        }


def process_attachments(
    file_paths: List[str],
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    registry_file: str = None
) -> Dict[str, Any]:
    """
    Process multiple attachment files in batch.
    
    Args:
        file_paths: List of file paths to process
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        registry_file: Path to document registry file for duplicate detection
    
    Returns:
        Dict with overall processing result:
            - 'total': int
            - 'successful': int
            - 'failed': int
            - 'total_chunks': int
            - 'results': List[Dict] - individual file results
    """
    if not file_paths:
        return {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'total_chunks': 0,
            'results': []
        }
    
    extracted_files = {}
    results = []
    
    # Load all files and extract content
    try:
        loaders = get_document_loader(file_paths)
        
        for file_path, loader in zip(file_paths, loaders):
            filename = os.path.basename(file_path)
            
            try:
                documents = loader.load()
                if documents:
                    content = '\n'.join([doc.page_content for doc in documents])
                    extracted_files[filename] = content
                    results.append({
                        'filename': filename,
                        'success': True,
                        'message': 'Loaded and ready for vectorization'
                    })
                else:
                    results.append({
                        'filename': filename,
                        'success': False,
                        'message': 'No content extracted'
                    })
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
                results.append({
                    'filename': filename,
                    'success': False,
                    'message': f"Error: {str(e)}"
                })
    
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return {
            'total': len(file_paths),
            'successful': 0,
            'failed': len(file_paths),
            'total_chunks': 0,
            'results': [{'filename': fp, 'success': False, 'message': str(e)} for fp in file_paths]
        }
    
    # Check if any files were loaded successfully
    if not extracted_files:
        logger.warning("No files loaded successfully")
        return {
            'total': len(file_paths),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'total_chunks': 0,
            'results': results
        }
    
    # Vectorize and store all files in Chroma
    try:
        ingestion_result = DocumentEmbeddingIngestion(
            extracted_files=extracted_files,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            registry_file=registry_file
        )
        
        total_chunks = ingestion_result.get('chunks_stored', 0) if ingestion_result.get('status') == 'success' else 0
        
        # Update results
        for result in results:
            if result['success']:
                result['message'] = f"Stored in Chroma DB ({total_chunks} total chunks)"
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        logger.info(f"Batch processing complete: {successful} successful, {failed} failed, {total_chunks} chunks stored")
        
        return {
            'total': len(file_paths),
            'successful': successful,
            'failed': failed,
            'total_chunks': total_chunks,
            'results': results
        }
    
    except Exception as e:
        logger.error(f"Error during vectorization: {e}")
        return {
            'total': len(file_paths),
            'successful': 0,
            'failed': len(file_paths),
            'total_chunks': 0,
            'results': results
        }

