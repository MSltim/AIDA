import sys
import os
import asyncio
import threading
import json
import tempfile
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.agents.supervisor.agent import setup_aida_workflow
from backend.src.utils.workflow_helper import process_query
from backend.src.utils.attachment_processor import process_attachments

app = Flask(__name__, 
            template_folder='frontend/pages',
            static_folder='frontend')

CORS(app)

# Paths for tool configuration files
MCP_SERVERS_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'src', 'tools', 'utils', 'mcp_servers.json')
ENABLED_TOOLS_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'src', 'tools', 'tools.json')

# Global variables to store the workflow
aida_app = None
config = {"configurable": {"thread_id": "web-session-1"}}
async_loop = None
loop_thread = None

# Current model settings
current_model_settings = {
    "provider": "azure",
    "model": os.getenv("AZURE_OPENAI_DEPLOYMENT_MODEL_NAME", "gpt-4o-ReCast"),
    "temperature": 0.3
}

def init_async_loop():
    """Initialize the async event loop in a separate thread"""
    global async_loop
    async_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(async_loop)
    async_loop.run_forever()

def initialize_workflow_sync(provider="azure", model=None, temperature=0.3, force_reinit=False):
    """Initialize the AIDA workflow with specified model settings"""
    global aida_app, current_model_settings
    
    if model is None:
        if provider == "google":
            model = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite")
        elif provider == "azure":
            model = os.getenv("AZURE_OPENAI_DEPLOYMENT_MODEL_NAME", "gpt-4o-ReCast")
        else:
            model = "gpt-4o-ReCast"
    
    # Check if settings changed
    settings_changed = (
        current_model_settings["provider"] != provider or
        current_model_settings["model"] != model or
        current_model_settings["temperature"] != temperature
    )
    
    # Reinitialize if: no app exists, settings changed, or force_reinit is True
    if aida_app is None or settings_changed or force_reinit:
        print(f"Initializing AIDA workflow with: {provider} | {model} | temp={temperature}")
        current_model_settings = {
            "provider": provider,
            "model": model,
            "temperature": temperature
        }
        future = asyncio.run_coroutine_threadsafe(
            setup_aida_workflow(provider=provider, model=model, temperature=temperature), 
            async_loop
        )
        aida_app = future.result(timeout=300)
        print("AIDA workflow initialized successfully")
    return aida_app

@app.route('/')
def index():
    """Render the landing page"""
    return render_template('landing.html')

@app.route('/agent_space.html')
def agent_space():
    """Render the agent space page"""
    return render_template('agent_space.html')

@app.route('/api/upload', methods=['POST'])
def upload_attachment():
    """Upload and vectorize file attachments"""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        # Create temporary files from uploaded data
        temp_file_paths = []
        for file in files:
            if file.filename:
                # Save to temporary location
                temp_dir = tempfile.gettempdir()
                filename = secure_filename(file.filename)
                temp_path = os.path.join(temp_dir, filename)
                file.save(temp_path)
                temp_file_paths.append(temp_path)
        
        if not temp_file_paths:
            return jsonify({'error': 'No valid files to process'}), 400
        
        # Process attachments through the vectorization pipeline
        result = process_attachments(
            file_paths=temp_file_paths,
            chunk_size=1000,
            chunk_overlap=100,
            registry_file=None
        )
        
        # Clean up temporary files
        for temp_path in temp_file_paths:
            try:
                os.remove(temp_path)
            except:
                pass
        
        return jsonify({
            'success': True,
            'total': result['total'],
            'successful': result['successful'],
            'failed': result['failed'],
            'total_chunks': result['total_chunks'],
            'results': result['results']
        })
    
    except Exception as e:
        print(f"Error uploading attachment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from frontend"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # Get model settings from request (with defaults)
        provider = data.get('provider', 'azure')
        if provider == "google":
            model = data.get('model', os.getenv('GOOGLE_LLM_MODEL', 'gemini-2.5-flash-lite'))
        elif provider == "azure":
            model = data.get('model', os.getenv('AZURE_OPENAI_DEPLOYMENT_MODEL_NAME', 'gpt-4o-ReCast'))
        else:
            model = data.get('model', 'gpt-4o-ReCast')
        temperature = float(data.get('temperature', 0.3))
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Initialize workflow with current settings
        initialize_workflow_sync(provider=provider, model=model, temperature=temperature)
        
        # Process the query in the async loop thread
        future = asyncio.run_coroutine_threadsafe(
            process_query(aida_app, user_message, config, debug=False),
            async_loop
        )
        response = future.result(timeout=300)
        
        return jsonify({
            'success': True,
            'response': response['final_message'],
            'metadata': {
                'routing_path': response['metadata']['routing_path'],
                'handled_by': response['metadata']['handled_by'],
                'model_settings': {
                    'provider': provider,
                    'model': model,
                    'temperature': temperature
                }
            }
        })
    
    except Exception as e:
        print(f"Error processing chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update model settings and reinitialize workflow"""
    try:
        data = request.get_json()
        provider = data.get('provider', 'azure')
        if provider == "google":
            model = data.get('model', os.getenv('GOOGLE_LLM_MODEL', 'gemini-2.5-flash-lite'))
        elif provider == "azure":
            model = data.get('model', os.getenv('AZURE_OPENAI_DEPLOYMENT_MODEL_NAME', 'gpt-4o-ReCast'))
        else:
            model = data.get('model', 'gpt-4o-ReCast')
        temperature = float(data.get('temperature', 0.3))
        
        # Reinitialize workflow with new settings
        initialize_workflow_sync(provider=provider, model=model, temperature=temperature, force_reinit=True)
        
        return jsonify({
            'success': True,
            'message': 'Settings applied successfully',
            'settings': {
                'provider': provider,
                'model': model,
                'temperature': temperature
            }
        })
    
    except Exception as e:
        print(f"Error updating settings: {e}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# TOOLS MANAGEMENT API
# =============================================================================

def load_mcp_servers():
    """Load all available MCP servers from mcp_servers.json"""
    try:
        if os.path.exists(MCP_SERVERS_PATH):
            with open(MCP_SERVERS_PATH, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading mcp_servers.json: {e}")
        return {}

def load_enabled_tools():
    """Load currently enabled tools from tools.json"""
    try:
        if os.path.exists(ENABLED_TOOLS_PATH):
            with open(ENABLED_TOOLS_PATH, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.load(open(ENABLED_TOOLS_PATH, 'r'))
        return {}
    except Exception as e:
        print(f"Error loading tools.json: {e}")
        return {}

def save_enabled_tools(tools):
    """Save enabled tools to tools.json"""
    try:
        with open(ENABLED_TOOLS_PATH, 'w') as f:
            json.dump(tools, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving tools.json: {e}")
        return False

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get all available tools with their enabled status"""
    try:
        all_servers = load_mcp_servers()
        enabled_tools = load_enabled_tools()
        
        tools_list = []
        for tool_id, config in all_servers.items():
            tools_list.append({
                'id': tool_id,
                'name': config.get('name', tool_id),
                'description': config.get('description', ''),
                'enabled': tool_id in enabled_tools,
                'requires_oauth': config.get('requires_oauth', False)
            })
        
        return jsonify({
            'success': True,
            'tools': tools_list
        })
    
    except Exception as e:
        print(f"Error getting tools: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools/<tool_id>', methods=['POST'])
def toggle_tool(tool_id):
    """Add or remove a tool from enabled tools"""
    try:
        data = request.get_json()
        action = data.get('action', 'add')  # 'add' or 'remove'
        
        print(f"Toggle tool request: {tool_id} - action: {action}")
        
        all_servers = load_mcp_servers()
        enabled_tools = load_enabled_tools()
        
        if tool_id not in all_servers:
            return jsonify({'error': f'Tool {tool_id} not found'}), 404
        
        if action == 'add':
            # Copy tool config from mcp_servers to tools.json
            enabled_tools[tool_id] = all_servers[tool_id]
            message = f'Tool {tool_id} added successfully'
            print(f"Added tool: {tool_id}")
        else:
            # Remove tool from tools.json
            if tool_id in enabled_tools:
                del enabled_tools[tool_id]
                print(f"Removed tool: {tool_id}")
            message = f'Tool {tool_id} removed successfully'
        
        # Save updated tools
        if save_enabled_tools(enabled_tools):
            print(f"Saved tools.json with {len(enabled_tools)} tools")
            
            # Reinitialize workflow with new tools (use current model settings)
            initialize_workflow_sync(
                provider=current_model_settings["provider"],
                model=current_model_settings["model"],
                temperature=current_model_settings["temperature"],
                force_reinit=True
            )
            
            return jsonify({
                'success': True,
                'message': message,
                'tool_id': tool_id,
                'enabled': action == 'add'
            })
        else:
            return jsonify({'error': 'Failed to save tools configuration'}), 500
    
    except Exception as e:
        print(f"Error toggling tool: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools/reload', methods=['POST'])
def reload_tools():
    """Reload workflow with current tools configuration"""
    try:
        # Force reinitialize workflow
        initialize_workflow_sync(force_reinit=True)
        
        return jsonify({
            'success': True,
            'message': 'Workflow reloaded with updated tools'
        })
    
    except Exception as e:
        print(f"Error reloading tools: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start the async event loop in a separate thread
    loop_thread = threading.Thread(target=init_async_loop, daemon=True)
    loop_thread.start()
    
    # Give the loop thread time to start
    import time
    time.sleep(0.5)
    
    # Initialize workflow
    initialize_workflow_sync()
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
