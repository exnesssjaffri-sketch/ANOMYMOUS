# Fix script for api/app.py
with open(r'C:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS\api\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """    # Get orchestrator
    orchestrator = _get_orchestrator()
    
    # In serverless, we execute synchronously (no background threads)
    # The orchestrator handles its own retry logic internally
    try:
        latest_result = orchestrator.execute_task(task_text)"""

new = """    # Get orchestrator
    orchestrator = _get_orchestrator()
    if orchestrator is None:
        return jsonify({
            "error": "No orchestrator available. Set ANOMYMOUS_USE_MOCK=1 for testing or configure API keys."
        }), 503
    
    # In serverless, we execute synchronously (no background threads)
    # The orchestrator handles its own retry logic internally
    try:
        latest_result = orchestrator.execute_task(task_text)"""

if old in content:
    content = content.replace(old, new)
    with open(r'C:\Users\ALI HAIDER\OneDrive\Desktop\ANOMYMOUS\api\app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Success')
else:
    print('Not found')