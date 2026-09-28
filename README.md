# ANOMYMOUS

A local AI-driven code execution and workspace management system for local development tasks.

## Overview

ANOMYMOUS is a complete workflow that:
- Takes natural language task descriptions
- Routes tasks to appropriate verification strategies (web, API, backend, testing, etc.)
- Executes code actions in a safe, isolated workspace
- Verifies results based on task classification

## Features

- **Task Classification**: Auto-detects task type (simple, frontend, backend, debugging, refactoring, testing, research, complex)
- **Safe Workspace Execution**: Isolated file operations with path traversal protection
- **Task Verification**: Purpose-built verifiers for different task categories
- **Local Router Integration**: Compatible with local LLM routers (e.g., http://127.0.0.1:31415/v1)

## Project Structure

```
ANOMYMOUS/
├── action_executor.py    # Executes file operations
├── llmapi_adapter.py     # LLM API client abstraction
├── orchestrator.py       # Main workflow coordinator
├── process_executor.py   # Process execution with safety checks
├── server.py             # HTTP dashboard server
├── transport.py          # Network transport abstraction (Mock/RealHTTP)
├── task_classifier.py    # Task type classification
├── verification.py       # Verification strategies
├── workspace_manager.py  # Safe workspace file management
├── static/               # UI assets
├── tests/                # Unit tests
├── workspace/            # Generated output directory
└── start_anonymous.bat   # Quick start script (Windows)
```

## Installation

No external dependencies required! Uses only Python standard library:
- `http.server` - For HTTP server
- `json` - JSON parsing
- `os` - File system operations
- `threading` - Concurrent task execution

## Quick Start

1. **Start the Server (Windows):**
   ```
   start_anonymous.bat
   ```

2. **Start the Server (Linux/Mac):**
   ```bash
   python server.py
   ```

3. **Access the Dashboard:**
   Open browser to: http://127.0.0.1:8000

4. **Submit a Task:**
   On the web interface, enter a task description and click "RUN".

## Local LLM Router Integration

ANOMYMOUS is designed to work with local LLM routers using the OpenAI-compatible API:

1. **Start a Local Router** (e.g., using `free-llm-api-server` or similar):
   ```
   free-llm-api-server
   ```

2. **Configure Environment Variables** (optional):
   ```
   set LLM_API_ENDPOINT=http://127.0.0.1:31415/v1
   set LLM_API_KEY=your-api-key-here
   ```

3. **Override Mock Transport in Server**:
   Modify `server.py` to pass `endpoint` and `api_key` to the Orchestrator.

## Available Tasks

You can request any of the following task types:
- **Simple Tasks**: Quick utility scripts or small changes
- **Frontend**: Build websites with HTML/CSS/JS
- **Backend**: API development with Python frameworks
- **Debugging**: Fix bugs in existing code
- **Refactoring**: Improve code structure
- **Testing**: Write or run test suites
- **Research**: Gather information or analyze data
- **Complex**: Large multi-component applications

## Running Tests

Run all tests:
```bash
python tests/test_task_classifier.py
python tests/test_orchestrator.py
python tests/test_recovery.py
python tests/test_llmapi_adapter.py
python tests/test_verification.py
```

## Safety & Security

- **Workspace Isolation**: All file operations are confined to the `workspace/` directory
- **Path Traversal Protection**: Attempts to escape workspace are blocked
- **Process Execution Control**: Only safe system commands are allowed
- **Fail-Closed Design**: System fails safely on errors rather than continuing with incomplete state

## License

This project is provided as-is for local development purposes.