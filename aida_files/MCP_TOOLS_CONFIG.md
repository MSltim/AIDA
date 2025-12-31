# MCP Tools Configuration Guide

This guide explains how to configure and set up each MCP (Model Context Protocol) tool for use with the AIDA application. Each tool requires specific credentials and setup steps.

## Atlassian Tools

### Overview
The Atlassian MCP provides access to **Confluence**, and **Trello** through a unified OAuth interface. AIDA has pre-configured OAuth credentials in .env file, so users only need to grant permissions the first time they use these tools.

### Prerequisites
- **Node.js** v18 or higher (for local testing)
- Atlassian Cloud accounts for:
  - Jira Cloud
  - Confluence Cloud (optional, if using Confluence features)
  - Trello (optional, if using Trello features)

### First-Time Setup (Browser Authorization)

**No manual credential entry required!** AIDA uses pre-configured OAuth credentials which should be in .env file.

#### How It Works:

1. **Load Atlassian Tools for the First Time:**
   - When you use Confluence, or Trello tools for the first time, AIDA will automatically redirect you to a browser tab

2. **Grant Permissions:**
   - You will see Atlassian's authorization screen asking for permission to:
     - Access your Confluence pages and spaces
     - Access your Trello boards and cards
   - Click **Allow** or **Grant** to authorize AIDA

3. **Automatic Authorization (Subsequent Uses):**
   - After the first authorization, AIDA will automatically use your account details
   - No re-authorization needed unless you revoke permissions
   - Your credentials are securely stored and managed by Atlassian OAuth

#### Confluence Integration

**Confluence Tool Functions:**
- Create, retrieve, and update pages
- Search across spaces
- Manage page hierarchies and attachments

#### Jira Integration

**Jira Tool Features:**
Jira integration is pre-configured—no setup needed beyond the first OAuth authorization!

**Capabilities:**
- **Project Management**
  - List all available Jira projects
  - Get detailed project information and metadata
  - View project settings and configurations

- **Issue Management**
  - Create new issues/tickets with custom fields
  - Set issue type (Bug, Story, Task, etc.)
  - Assign priorities (High, Medium, Low)
  - Assign issues to team members
  - Add descriptions and issue details

- **Issue Tracking**
  - Search and filter issues
  - Update issue status and comments
  - Track issue history and changes
  - Add attachments and links to issues

**How It Works:**
- Simply authorize once when you first use Jira features
- After that, AIDA automatically uses your Jira account
- All operations are performed directly on your Jira instance
- Results are formatted and presented to the LLM

#### Trello Integration

**Trello Tool Features:**
Trello integration is pre-configured—no setup needed beyond the first OAuth authorization!

**Capabilities:**
- **Board Management**
  - Access and view all your Trello boards
  - Get board details and configuration
  - List all lists within a board

- **Card Management**
  - Create new cards on lists
  - Update card titles and descriptions
  - Move cards between lists
  - Delete cards

- **Team Collaboration**
  - Assign team members to cards
  - Set due dates and reminders
  - Add labels and categories
  - Add comments and attachments
  - Set card priorities and complexity

- **List Organization**
  - Organize lists within boards
  - Archive completed items
  - Create checkboxes and subtasks

**How It Works:**
- Simply authorize once when you first use Trello features
- After that, AIDA automatically uses your Trello account
- All operations are performed directly on your Trello boards
- Results are formatted and presented to the LLM

## PowerBI Modeling MCP

### Overview
PowerBI Modeling MCP is not included in the repository and must be downloaded separately. It is automatically installed during Docker container initialization, but for local development, follow the manual installation steps below.

### Download Link

**Download the PowerBI Modeling MCP .vsix file:**
- [PowerBI Modeling MCP Download Link](https://your-organization-download-link/powerbi_modeling_mcp.vsix)
- *(Contact your organization administrator if the link is not accessible)*

### Setup Instructions

#### Manual Installation (For Local Development)

1. **Download the .vsix file:**
   - Use the download link above to obtain the PowerBI Modeling MCP .vsix file
   - Save it to your local system (e.g., `C:\Downloads\powerbi_modeling_mcp.vsix`)

2. **Extract the file:**
   ```cmd
   REM Rename the .vsix file to .zip
   
   REM Extract the contents (using built-in tar command in Windows 10+)
   
   REM Or use 7-Zip/WinRAR if tar is not available
   ```

3. **Rename and move the extracted folder:**
   ```cmd
   REM Rename the extracted folder to match expected name
   ren C:\temp\powerbi_extract powerbi_modeling_mcp
   
   REM Move to custom_mcp directory
   move C:\temp\powerbi_extract\powerbi_modeling_mcp 
   C:\****\**\***\AIDA\backend\src\tools\custom_mcp\powerbi_modeling_mcp
   ```

4. **Verify installation:**
   - Ensure the folder structure looks like:
     ```
     backend/src/tools/custom_mcp/
     ├── powerbi_modeling_mcp/
     │   ├── __init__.py
     │   ├── agent.py
     │   └── ...
     ├── Jira_mcp.py
     ├── trello_mcp.py
     └── ...
     ```

## RAG MCP (Retrieval-Augmented Generation)

### Overview
RAG MCP provides semantic search and document retrieval capabilities using ChromaDB for vector embeddings. This tool is pre-configured and ready to use—no setup required!

### Features
- **Semantic Search**: Search across documents using natural language queries
- **Vector Embeddings**: Store and retrieve document embeddings for similarity matching
- **Document Chunking**: Automatically process and chunk documents for efficient retrieval
- **Query Augmentation**: Enhance queries with context for improved results
- **Multi-format Support**: Handle various document formats (PDFs, text files, etc.)
- **Contextual Retrieval**: Return relevant document snippets with context

### How It Works
- Documents are automatically indexed in ChromaDB vector database
- When you ask a question, the tool searches for semantically similar documents
- Retrieved documents are provided as context to the LLM for accurate answers
- No manual configuration needed—just use it!

---

## SQL MCP

### Overview
SQL MCP provides intelligent SQL query analysis, optimization, and execution capabilities. This tool is pre-configured and ready to use—no setup required!

### Features
- **Query Optimization**: Analyze SQL queries and receive optimization recommendations
- **Anti-pattern Detection**: Identify performance issues like SELECT *, inefficient JOINs, correlated subqueries
- **Dialect Support**: Works with multiple SQL dialects (BigQuery, Snowflake, PostgreSQL, MySQL, SQLite, Oracle, SQL Server)
- **Query Formatting**: Automatically format and beautify SQL queries for readability
- **Complexity Analysis**: Calculate query complexity scores and provide improvement suggestions
- **Index Suggestions**: Get recommendations for creating indexes to improve performance
- **Query Execution**: Execute SQL queries and retrieve results (when database is connected)
- **Performance Metrics**: Analyze query execution plans and performance bottlenecks

### How It Works
- Submit a SQL query with an optional dialect specification
- The tool analyzes the query for common performance anti-patterns
- Receives detailed recommendations for optimization
- Get formatted, optimized query suggestions
- No database credentials needed for analysis—just provide the SQL query!


## File Read MCP

### Overview
File Read MCP provides secure file reading and document processing capabilities. This tool is pre-configured and ready to use—no setup required!

### Features
- **Secure File Reading**: Read files from specified paths with built-in security validation
- **Multi-format Support**: Handle various document types:
  - Text files (TXT, MD, LOG)
  - Documents (PDF, DOCX, PPTX)
  - Data files (JSON, CSV, XML, YAML)
  - Code files (PY, JS, TS, Java, etc.)
- **Automatic Format Detection**: Intelligently detect file type and extract content accordingly
- **Content Extraction**: Extract text and structure from complex documents
- **Safe Path Validation**: Prevent unauthorized file access with built-in security checks
- **Encoding Handling**: Automatically handle different file encodings
- **Content Formatting**: Return formatted, readable content ready for LLM processing

### How It Works
- Simply provide the file path (absolute or relative)
- The tool automatically detects the file type and format
- Content is extracted and formatted for easy reading
- Returns clean, structured content without setup or configuration

---

## Utilities MCP

### Overview
Utilities MCP provides general utility functions for system operations and data manipulation. This tool is pre-configured and ready to use—no setup required!

### Features
- **String Manipulation**: Process, transform, and analyze text strings
- **Data Formatting**: Format data for display and export (JSON, CSV, tables)
- **File Operations**: Copy, move, rename, and organize files
- **System Utilities**: Execute system commands and retrieve system information
- **Data Validation**: Validate data types, formats, and integrity
- **Text Processing**: Parse, extract, and transform text content
- **Encoding/Decoding**: Handle base64, URL encoding, and other encoding formats
- **Date/Time Operations**: Format and manipulate dates and timestamps

---

## Additional Resources

- [Atlassian Developer Documentation](https://developer.atlassian.com/)
- [Jira Cloud API Reference](https://developer.atlassian.com/cloud/jira/rest/v3/)
- [Trello API Documentation](https://developer.atlassian.com/cloud/trello/rest/api-group-actions/)
- [Power BI Developer Portal](https://powerbi.microsoft.com/en-us/developers/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
