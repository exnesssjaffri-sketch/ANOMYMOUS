# ANONYMOUS PHASE-2 STATE MAP

## Project Root
- **Root Directory:** `C:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS`

## Entry Point
- **Main Script:** `anomyous.ps1`, `anomyous_fixed.ps1`

## Source Files
- **Python Files:**
  - `failure_recovery.py`
  - `multi_worker_executor.py`
  - `task_classifier.py`
  - `verification.py`
  - `worker_registry.py`
  - `worker_router.py`
  - `workspace_detector.py`

- **PowerShell Scripts:**
  - `workspace_detector.ps1`

- **Batch Script:**
  - `run_test.bat`

## Worker Registry
- **FCC:** Command `fcc`, capabilities: `implementation`, `simple coding`, `website creation`, `bug fixes`
- **Claude:** Command `claude`, capabilities: `architecture`, `complex reasoning`, `debugging`, `code review`
- **OpenCode:** Command `opencode`, capabilities: `implementation`, `frontend`, `full-stack`, `refactoring`

## Workspace Detection
- **Detects:** Node.js, Python, Rust, Go, PHP, Ruby, Java, Static Website, Git Repository
- **Logic:** Checks for specific project indicators and Git repository status

## Task Classification
- **Classification Logic:**
  - Simple tasks: `change`, `fix`
  - Medium tasks: `website`, `button`, `debug`, `error`
  - Complex tasks: `dashboard`, `SaaS`
  - Debugging tasks: `debug`, `error`
  - Refactoring tasks: `refactor`
  - Research tasks: `research`
  - Testing tasks: `test`

## Capability Routing
- **Worker Selection:** Selects the worker with the least capability overlap
- **Escalation:** If the best worker fails, escalates to the next available worker

## Verification System
- **Verification Logic:** Checks for existence of required files, valid HTML, JS, CSS, imports, build success, and browser verification

## Failure Recovery
- **Recovery Logic:** Generates repair tasks for errors and writes them to a file

## Tests
- **Test Files:**
  - `test_task_classification.py`
  - `test_workspace_detector.py`

## Configuration
- **No explicit configuration files found**

## Documentation
- **No existing documentation files found**