/**
 * ANOMYMOUS Dashboard Frontend
 * Handles UI interactions and API communication
 */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('ANOMYMOUS Dashboard initialized');
    
    // Load capabilities
    await loadCapabilities();
    
    // Load providers
    await loadProviders();
    
    // Load analytics
    await loadAnalytics();
    
    // Setup task submission
    setupTaskSubmission();
});

/**
 * Load and display capabilities
 */
async function loadCapabilities() {
    try {
        const response = await fetch('/capabilities');
        const data = await response.json();
        
        const capabilitiesDiv = document.querySelector('.capabilities-content') || 
                                document.querySelector('[data-section="capabilities"]');
        
        if (capabilitiesDiv) {
            let html = '<ul style="list-style: none; padding: 0;">';
            html += `<li>✅ Local Filesystem: ${data.local_filesystem ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Subprocess Execution: ${data.subprocess_execution ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Workspace Operations: ${data.workspace_operations ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Background Tasks: ${data.background_tasks ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Persistent State: ${data.persistent_state ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Cloud Deployment: ${data.cloud_deployment ? 'Yes' : 'No'}</li>`;
            html += '</ul>';
            html += `<p><em>${data.note}</em></p>`;
            capabilitiesDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading capabilities:', error);
        const capabilitiesDiv = document.querySelector('.capabilities-content') || 
                                document.querySelector('[data-section="capabilities"]');
        if (capabilitiesDiv) {
            capabilitiesDiv.innerHTML = `<p style="color: red;">Error loading capabilities: ${error.message}</p>`;
        }
    }
}

/**
 * Load and display LLM providers
 */
async function loadProviders() {
    try {
        const response = await fetch('/providers');
        const data = await response.json();
        
        const providersDiv = document.querySelector('.providers-content') || 
                             document.querySelector('[data-section="providers"]');
        
        if (providersDiv && data.providers && data.providers.length > 0) {
            let html = `<p>Available Providers: <strong>${data.count}</strong></p>`;
            html += '<ul>';
            data.providers.forEach(provider => {
                html += `
                    <li>
                        <strong>${provider.display_name}</strong>
                        <br/>
                        <small>Provider: ${provider.name} | Models: ${provider.model_count}</small>
                    </li>
                `;
            });
            html += '</ul>';
            providersDiv.innerHTML = html;
        } else if (providersDiv) {
            providersDiv.innerHTML = '<p>No providers configured. Add API keys to enable.</p>';
        }
    } catch (error) {
        console.error('Error loading providers:', error);
        const providersDiv = document.querySelector('.providers-content') || 
                             document.querySelector('[data-section="providers"]');
        if (providersDiv) {
            providersDiv.innerHTML = `<p style="color: red;">Error loading providers: ${error.message}</p>`;
        }
    }
}

/**
 * Load and display analytics
 */
async function loadAnalytics() {
    try {
        const response = await fetch('/analytics');
        const data = await response.json();
        
        const analyticsDiv = document.querySelector('.analytics-content') || 
                             document.querySelector('[data-section="analytics"]');
        
        if (analyticsDiv) {
            let html = '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px;">';
            html += JSON.stringify(data, null, 2);
            html += '</pre>';
            analyticsDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        const analyticsDiv = document.querySelector('.analytics-content') || 
                             document.querySelector('[data-section="analytics"]');
        if (analyticsDiv) {
            analyticsDiv.innerHTML = `<p style="color: red;">Error loading analytics: ${error.message}</p>`;
        }
    }
}

/**
 * Setup task submission handler
 */
function setupTaskSubmission() {
    // Find the RUN button and task input
    const buttons = document.querySelectorAll('button');
    let runButton = null;
    
    for (let btn of buttons) {
        if (btn.textContent.includes('RUN')) {
            runButton = btn;
            break;
        }
    }
    
    const taskInput = document.querySelector('input[type="text"]');
    
    if (!runButton || !taskInput) {
        console.warn('Run button or task input not found');
        return;
    }
    
    runButton.addEventListener('click', async (e) => {
        e.preventDefault();
        
        const taskText = taskInput.value.trim();
        
        if (!taskText) {
            alert('Please enter a task description');
            return;
        }
        
        await submitTask(taskText, runButton);
    });
    
    // Allow Enter key to submit
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            runButton.click();
        }
    });
}

/**
 * Submit a task and handle the response
 */
async function submitTask(taskText, runButton) {
    const originalText = runButton.textContent;
    runButton.disabled = true;
    runButton.textContent = 'Running...';
    
    try {
        const response = await fetch('/task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ task: taskText })
        });
        
        const data = await response.json();
        
        if (response.ok || response.status === 202) {
            updateExecutionStatus('✅ Task submitted. Processing...');
            
            // Poll for status every 2 seconds (max 30 seconds)
            let attempts = 0;
            const maxAttempts = 15;
            
            const pollInterval = setInterval(async () => {
                attempts++;
                
                try {
                    const statusResponse = await fetch('/status');
                    const statusData = await statusResponse.json();
                    
                    if (statusData.status && statusData.status !== 'no_result') {
                        clearInterval(pollInterval);
                        
                        let html = '<div style="background: #f0f0f0; padding: 10px; border-radius: 4px;">';
                        html += '<h4>Task Result:</h4>';
                        html += '<pre style="overflow: auto; max-height: 300px;">';
                        html += JSON.stringify(statusData, null, 2);
                        html += '</pre>';
                        html += '</div>';
                        
                        updateExecutionStatus(html);
                    } else if (attempts >= maxAttempts) {
                        clearInterval(pollInterval);
                        updateExecutionStatus('⏱️ Task is taking longer than expected. Check back soon.');
                    }
                } catch (error) {
                    console.error('Error polling status:', error);
                }
            }, 2000);
        } else {
            updateExecutionStatus(`❌ Error: ${data.error || 'Unknown error'} (Status: ${response.status})`);
        }
    } catch (error) {
        console.error('Error submitting task:', error);
        updateExecutionStatus(`❌ Error: ${error.message}`);
    } finally {
        runButton.disabled = false;
        runButton.textContent = originalText;
    }
}

/**
 * Update execution status display
 */
function updateExecutionStatus(message) {
    const statusDiv = document.querySelector('.status-content') || 
                      document.querySelector('[data-section="status"]');
    
    if (statusDiv) {
        statusDiv.innerHTML = message;
    } else {
        console.warn('Status display element not found');
    }
}
