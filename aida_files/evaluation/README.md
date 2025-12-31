# AIDA Promptfoo Evaluation

This directory contains the Promptfoo evaluation setup for testing the AIDA multi-agent system.

## Files

- `provider.py` - Custom Python provider that calls the AIDA API
- `promptfooconfig.yaml` - Main evaluation configuration with test cases
- `redteam.yaml` - Red team security testing configuration
- `requirements.txt` - Python dependencies for the provider

## Prerequisites

1. **Install Promptfoo** (if not already installed):
   ```bash
   npm install -g promptfoo
   ```

2. **Install Python dependencies**:
   ```bash
   cd evaluation
   pip install -r requirements.txt
   ```

3. **Ensure AIDA is running**:
   ```bash
   cd ..
   python aida.py
   ```
   The API should be accessible at `http://localhost:5000`

## Running Evaluations

### Standard Evaluation

Run the main evaluation tests:

```bash
cd evaluation
npx promptfoo eval
```

View results in the web UI:

```bash
npx promptfoo view
```

### Red Team Testing

Run security and safety tests:

```bash
npx promptfoo redteam run --config redteam.yaml
```

View red team results:

```bash
npx promptfoo redteam report
```

## Test Categories

### Standard Evaluation (`promptfooconfig.yaml`)

1. **Developer Tasks** - Code generation, debugging, CI/CD help
2. **Project Management** - Jira issue creation, sprint planning, Azure DevOps
3. **RAG Queries** - Knowledge base searches, documentation queries
4. **Multi-tool Coordination** - Complex tasks requiring multiple agents
5. **Error Handling** - Graceful handling of ambiguous or impossible requests

### Red Team Testing (`redteam.yaml`)

1. **Prompt Injection** - Tests for instruction override attacks
2. **Data Leakage** - Tests for PII and credential exposure
3. **Harmful Content** - Tests for refusal of malicious requests
4. **Jailbreak Attempts** - Tests for safety bypass attempts
5. **Excessive Agency** - Tests for unauthorized action prevention
6. **Hallucination** - Tests for false capability claims

## Configuration Options

### Provider Settings

Edit `provider.py` to configure:

- `API_BASE_URL` - AIDA API endpoint (default: `http://localhost:5000`)
- Timeout settings
- Authentication headers (if required)

### Test Customization

Edit `promptfooconfig.yaml` to:

- Add new test cases
- Modify assertions
- Change pass thresholds
- Add custom variables

## Sample Output

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Eval Results                                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Test Cases:     12                                                           │
│ Passed:         10                                                           │
│ Failed:         2                                                            │
│ Pass Rate:      83.3%                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### API Connection Error

If you see connection errors:
1. Verify AIDA is running: `curl http://localhost:5000/api/tools`
2. Check the API_BASE_URL in provider.py
3. Ensure no firewall is blocking localhost:5000

### Import Errors

If Python imports fail:
1. Activate your virtual environment
2. Run `pip install -r requirements.txt`
3. Verify Python version (3.8+ required)

### Slow Tests

If tests are timing out:
1. Increase timeout in provider.py
2. Add delay between tests in the config
3. Check AIDA logs for performance issues

## Further Reading

- [Promptfoo Documentation](https://www.promptfoo.dev/docs/)
- [LangGraph Evaluation Guide](https://www.promptfoo.dev/docs/guides/evaluate-langgraph/)
- [Red Team Testing](https://www.promptfoo.dev/docs/red-team/)
