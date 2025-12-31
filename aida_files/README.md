# Project Name

A comprehensive AI-powered application with backend services, frontend interface, and evaluation capabilities.

## Project Structure

```
.
├── aida.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── backend/               # Backend services
│   └── src/
│       ├── agents/        # AI agents (supervisor and sub-agents)
│       ├── chroma_db/     # Vector database for embeddings
│       ├── evaluations/   # Model evaluation and testing
│       ├── tools/         # MCP tools and utilities
│       │   ├── mcp_client.py
│       │   └── custom_mcp/
│       ├── usecase/       # Use case configurations
│       └── utils/         # Utility functions
├── frontend/              # Frontend application
│   └── pages/
│       └── landing.html
└── storage/              # Resource storage
```

## Getting Started

### Prerequisites
- Python 3.8+
- Required dependencies (see `requirements.txt`)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python aida.py
```

## Key Components

- **Agents**: Supervisor and sub-agent implementations for AI task execution
- **Chroma DB**: Vector database for semantic search and embeddings
- **Tools**: MCP client integration with custom tools
- **Evaluations**: Testing and evaluation framework for model performance
- **Frontend**: Landing page interface for user interaction

## Configuration

Configuration files are located in `backend/src/usecase/config.json`

## Tools and Integrations

- MCP (Model Context Protocol) client integration
- Custom tool definitions in `backend/src/tools/tools.json`