# =============================================================================
# Input File Handler - Multi-Format Document Loading & Processing
# =============================================================================
#
# Description:
#   Handles loading and processing of multiple document formats including
#   PDF, DOCX, TXT, Markdown, and HTML. Integrates with LangChain document
#   loaders to normalize diverse input sources into consistent document format.
#
# Architecture:
#   - Multi-format document loader integration (LangChain)
#   - File type detection and format-specific handling
#   - Document metadata extraction and normalization
#   - Batch processing capabilities for multiple files
#   - Error handling and logging for document processing
#
# Credits:
#   - Developed by: Siraj, Aman, Dasari Harsha Sri Ram, Ranjithkumar S
#   - LangChain: Document loaders integration
#   - Integration: AIDA Data Governance Platform
#
# Version: 1.0.0
# Date: November 2025

# =============================================================================

import os
import sys
import pandas as pd
from typing import List, Dict, Any, Callable

# Add the parent directory to sys.path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import get_logger
from langchain_community.document_loaders import (
    TextLoader,           
    PyPDFLoader,         
    UnstructuredWordDocumentLoader,            
    UnstructuredMarkdownLoader,      
    UnstructuredODTLoader,                   
    BSHTMLLoader,              
)

logger = get_logger(__name__)


FILE_TYPES = {
    # Document Files
    '.pdf': ('PDF Document', 'PDF extraction'),
    '.txt': ('Text File', 'Text reading with metadata'),
    '.md': ('Markdown Document', 'Markdown parsing'),
    '.rtf': ('Rich Text Format', 'RTF parsing'),
    '.odt': ('OpenDocument Text', 'ODT parsing'),
    '.docx': ('Microsoft Word Document', 'Word parsing'),

    # Data Files
    '.csv': ('CSV Data File', 'CSV data analysis with full content'),
    '.xlsx': ('Microsoft Excel Spreadsheet', 'Excel multi-sheet analysis with full content'),
    '.json': ('JSON Data File', 'JSON structured parsing with full content'),
    '.xml': ('XML Document', 'XML parsing with full content'),
    '.yaml': ('YAML Configuration', 'YAML text reading with metadata'),
    '.yml': ('YAML Configuration', 'YAML text reading with metadata'),

    # Web & Database
    '.html': ('HTML Web Page', 'HTML parsing'),
    '.sql': ('SQL Database Script', 'SQL script analysis with full code'),

    # Programming Languages
    '.py': ('Python Code', 'Python code analysis with full source'),
    '.js': ('JavaScript Code', 'Code text extraction with metadata'),
    '.java': ('Java Code', 'Code text extraction with metadata'),
    '.cpp': ('C++ Code', 'Code text extraction with metadata'),
    '.c': ('C Code', 'Code text extraction with metadata'),
    '.cs': ('C# Code', 'Code text extraction with metadata'),
    '.php': ('PHP Code', 'Code text extraction with metadata'),
    '.go': ('Go Code', 'Code text extraction with metadata'),
    '.rs': ('Rust Code', 'Code text extraction with metadata'),

    # Scripts
    '.sh': ('Shell Script', 'Script text extraction with metadata'),
    '.bat': ('Batch Script', 'Script text extraction with metadata'),
    '.ps1': ('PowerShell Script', 'Script text extraction with metadata')
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_file_info(suffix: str) -> tuple:
    """Retrieves the file type description and processing method for a given suffix."""
    return FILE_TYPES.get(suffix.lower(), (f'Unsupported File ({suffix})', 'No processing method available'))

def get_file_type_description(suffix: str) -> str:
    """Retrieves just the file type description."""
    return get_file_info(suffix)[0]

def get_processing_method(suffix: str) -> str:
    """Retrieves just the processing method description."""
    return get_file_info(suffix)[1]

# ============================================================================
# HELPER FOR ENHANCED PROCESSING
# ============================================================================

def _create_loader_from_content(content_lines: List[str], base_file_path: str) -> TextLoader:
    """Writes content to a temporary text file and returns a TextLoader for it."""
    temp_path = base_file_path + ".txt"
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))
    return TextLoader(temp_path, encoding='utf-8')

# ============================================================================
# ENHANCED DOCUMENT PROCESSOR FUNCTIONS
# ============================================================================

def process_excel_file(file_path: str, filename: str) -> TextLoader:
    """
    Processes an Excel file, extracting data from all sheets.
    Raises an exception if the file cannot be processed by pandas.
    """
    excel_data = pd.ExcelFile(file_path)
    content = [f"Excel File: {filename}", f"Total Sheets: {len(excel_data.sheet_names)}", "=" * 50]
    for sheet in excel_data.sheet_names:
        try:
            df = pd.read_excel(excel_data, sheet_name=sheet)
            content.extend([
                f"\n--- Sheet: {sheet} ---",
                f"Columns: {', '.join(df.columns.astype(str))}",
                f"Rows: {len(df)}",
                "\nComplete Data:",
                df.to_string(index=False) if not df.empty else "Sheet is empty."
            ])
        except Exception as e:
            content.append(f"\n--- Sheet: {sheet} ---: Error reading sheet: {e}")
    return _create_loader_from_content(content, file_path)

def process_csv_file(file_path: str, filename: str) -> TextLoader:
    """
    Processes a CSV file, providing metadata and full data.
    Raises an exception if the file cannot be parsed by pandas.
    """
    df = pd.read_csv(file_path)
    content = [
        f"CSV File: {filename}",
        f"Rows: {len(df)}, Columns: {len(df.columns)}",
        f"Column Names: {', '.join(df.columns.astype(str))}",
        "=" * 50,
        "Complete Data:",
        df.to_string(index=False)
    ]
    return _create_loader_from_content(content, file_path)

def process_code_or_text_file(file_path: str, filename: str, file_type: str) -> TextLoader:
    """
    Generic processor for code, scripts, and plain text files.
    Raises an exception if the file cannot be read.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    lines = file_content.split('\n')
    content = [
        f"{file_type} File: {filename}",
        f"Total Lines: {len(lines)}",
        "=" * 50,
        file_content
    ]
    return _create_loader_from_content(content, file_path)

def process_json_file(file_path: str, filename: str) -> TextLoader:
    """Processes a JSON file, preserving its structure and content."""
    return process_code_or_text_file(file_path, filename, "JSON")

def process_xml_file(file_path: str, filename: str) -> TextLoader:
    """Processes an XML file, preserving its structure and content."""
    return process_code_or_text_file(file_path, filename, "XML")


def get_document_loader(file_paths: List[str]) -> List[Any]:
    """
    Selects the appropriate document loaders for a list of file paths based on their extensions.
    Filenames are automatically extracted from the file paths.
    This function processes multiple files and returns a list of loaders.
    It is strict and will raise an exception for unsupported file types
    or for files that fail to load, as all fallbacks have been removed.
    """
    logger.info(f"Starting to process {len(file_paths)} file(s) for document loaders.")
    loaders = []
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        suffix = os.path.splitext(filename)[1].lower()
        logger.debug(f"Processing file: {filename} with extension: {suffix}")

        # Mapping of file extensions to their dedicated processing functions
        ENHANCED_PROCESSORS: Dict[str, Callable[[str, str], TextLoader]] = {
            '.xlsx': process_excel_file,
            '.csv': process_csv_file,
            '.json': process_json_file,
            '.xml': process_xml_file,
            '.py': lambda p, f: process_code_or_text_file(p, f, 'Python'),
            '.sql': lambda p, f: process_code_or_text_file(p, f, 'SQL'),
            '.yaml': lambda p, f: process_code_or_text_file(p, f, 'YAML'),
            '.yml': lambda p, f: process_code_or_text_file(p, f, 'YAML'),
            '.js': lambda p, f: process_code_or_text_file(p, f, 'JavaScript'),
            '.java': lambda p, f: process_code_or_text_file(p, f, 'Java'),
            '.c': lambda p, f: process_code_or_text_file(p, f, 'C'),
            '.cpp': lambda p, f: process_code_or_text_file(p, f, 'C++'),
            '.cs': lambda p, f: process_code_or_text_file(p, f, 'C#'),
            '.go': lambda p, f: process_code_or_text_file(p, f, 'Go'),
            '.rs': lambda p, f: process_code_or_text_file(p, f, 'Rust'),
            '.php': lambda p, f: process_code_or_text_file(p, f, 'PHP'),
            '.sh': lambda p, f: process_code_or_text_file(p, f, 'Shell Script'),
            '.bat': lambda p, f: process_code_or_text_file(p, f, 'Batch Script'),
            '.ps1': lambda p, f: process_code_or_text_file(p, f, 'PowerShell Script'),
            '.txt': lambda p, f: process_code_or_text_file(p, f, 'Text')
        }

        # Standard LangChain loaders for common document types
        STANDARD_LOADERS: Dict[str, Callable[[str], Any]] = {
            '.pdf': PyPDFLoader,
            '.docx': UnstructuredWordDocumentLoader,
            '.md': UnstructuredMarkdownLoader,
            '.odt': UnstructuredODTLoader,
            '.html': BSHTMLLoader,
        }

        # 1. Check for an enhanced processor
        if suffix in ENHANCED_PROCESSORS:
            loaders.append(ENHANCED_PROCESSORS[suffix](file_path, filename))
        # 2. Check for a standard loader
        elif suffix in STANDARD_LOADERS:
            loaders.append(STANDARD_LOADERS[suffix](file_path))
        # 3. If no loader is found, raise an error.
        else:
            logger.error(f"No loader implemented for file type: '{suffix}' for file '{filename}'")
            raise NotImplementedError(f"No loader is implemented for the file type: '{suffix}' for file '{filename}'")
    
    logger.info(f"Successfully created {len(loaders)} document loader(s).")
    return loaders


if __name__ == "__main__":
    logger.info("Starting test of get_document_loader function.")
    # Test the get_document_loader function with a list of sample file paths
    # Filenames are automatically extracted from the paths
    file_paths = [r"C:\Users\10822231\Workspace\DA\Archetypes_MVP_2\README.md"]  # Example: list of file paths
    
    try:
        loaders = get_document_loader(file_paths)
        for i, loader in enumerate(loaders):
            documents = loader.load()
            filename = os.path.basename(file_paths[i])
            print(f"Successfully loaded {len(documents)} document(s) from '{filename}'.")
            if documents:
                print("\nFirst document preview:")
                print(documents[0].page_content[:500])  # Print first 500 characters
            else:
                print("No content loaded.")
            print("-" * 50)
        logger.info("Test completed successfully.")
    except Exception as e:
        logger.error(f"Error during test: {e}")
        print(f"Error loading files: {e}")