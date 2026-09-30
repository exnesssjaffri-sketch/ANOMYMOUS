/**
 * ANOMYMOUS Dashboard Frontend
 * Handles UI interactions and API communication
 */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('ANOMYMOUS Dashboard initialized');
    
    // Load all data
    await loadCapabilities();
    await loadProviders();
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
        
        // Target the correct element ID from index.html
        const capGrid = document.getElementById('capabilitiesGrid');
        
        if (capGrid) {
            let html = '<ul style="list-style: none; padding: 0; margin: 0;">';
            html += `<li>✅ Local Filesystem: ${data.local_filesystem ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Subprocess Execution: ${data.subprocess_execution ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Workspace Operations: ${data.workspace_operations ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Background Tasks: ${data.background_tasks ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Persistent State: ${data.persistent_state ? 'Yes' : 'No'}</li>`;
            html += `<li>✅ Cloud Deployment: ${data.cloud_deployment ? 'Yes' : 'No'}</li>`;
            html += '</ul>';
            html += `<p style="font-size: 0.9em; color: #666;"><em>${data.note}</em></p>`;
            capGrid.innerHTML = html;
            console.log('Capabilities loaded:', data);
        } else {
            console.warn('Capabilities grid element not found');
        }
    } catch (error) {
        console.error('Error loading capabilities:', error);
        const capGrid = document.getElementById('capabilitiesGrid');
        if (capGrid) {
            capGrid.innerHTML = `<p style="color: red;">Error loading capabilities: ${error.message}</p>`;
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
        
        // Target the correct element ID from index.html
        const providersList = document.getElementById('providersList');
        
        if (providersList) {
            if (data.providers && data.providers.length > 0) {
                let html = `<p><strong>Available Providers: ${data.count}</strong></p>`;
                html += '<ul style="list-style: none; padding: 0;">';
                data.providers.forEach(provider => {
                    html += `
                        <li style="margin-bottom: 10px; padding: 8px; background: #f9f9f9; border-radius: 4px;">
                            <strong>${provider.display_name}</strong>
                            <br/>
                            <small style="color: #666;">
                                ${provider.name} | ${provider.model_count} models
                            </small>
                        </li>
                    `;
                });
                html += '</ul>';
                providersList.innerHTML = html;
                console.log('Providers loaded:', data);
            } else {
                providersList.innerHTML = '<p style="color: #999;">No providers configured. Add API keys to enable.</p>';
                console.log('No providers available');
            }
        } else {
            console.warn('Providers list element not found');
        }
    } catch (error) {
        console.error('Error loading providers:', error);
        const providersList = document.getElementById('providersList');
        if (providersList) {
            providersList.innerHTML = `<p style="color: red;">Error loading providers: ${error.message}</p>`;
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
        
        // Target the correct element ID from index.html
        const analyticsGrid = document.getElementById('analyticsGrid');
        
        if (analyticsGrid) {
            let html = '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow: auto; max-height: 250px; font-size: 0.85em;">';
            html += JSON.stringify(data, null, 2);
            html += '</pre>';
            analyticsGrid.innerHTML = html;
            console.log('Analytics loaded:', data);
        } else {
            console.warn('Analytics grid element not found');
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        const analyticsGrid = document.getElementById('analyticsGrid');
        if (analyticsGrid) {
            analyticsGrid.innerHTML = `<p style="color: red;">Error loading analytics: ${error.message}</p>`;
        }
    }
}

/**
 * Setup task submission handler
 */
function setupTaskSubmission() {
    // Get elements by their IDs from index.html
    const taskInput = document.getElementById('taskInput');
    const runBtn = document.getElementById('runBtn');
    const statusOutput = document.getElementById('statusOutput');
    
    if (!taskInput || !runBtn || !statusOutput) {
        console.warn('Task submission elements not found', {
            taskInput: !!taskInput,
            runBtn: !!runBtn,
            statusOutput: !!statusOutput
        });
        return;
    }
    
    // Click handler
    runBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        const taskText = taskInput.value.trim();
        
        if (!taskText) {
            alert('Please enter a task description');
            return;
        }
        
        await submitTask(taskText, runBtn, statusOutput);
    });
    
    // Enter key handler
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            runBtn.click();
        }
    });
    
    console.log('Task submission setup complete');
}

/**
 * Submit a task and handle the response
 */
async function submitTask(taskText, runBtn, statusOutput) {
    const originalText = runBtn.textContent;
    runBtn.disabled = true;
    runBtn.textContent = 'Running...';
    statusOutput.textContent = '⏳ Submitting task...';
    
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
            statusOutput.textContent = '✅ Task submitted. Processing...';
            
            // Poll for status every 2 seconds
            let attempts = 0;
            const maxAttempts = 15;
            
            const pollInterval = setInterval(async () => {
                attempts++;
                
                try {
                    const statusResponse = await fetch('/status');
                    const statusData = await statusResponse.json();
                    
                    // Update display
                    if (statusData.status && statusData.status !== 'no_result') {
                        clearInterval(pollInterval);
                        statusOutput.textContent = JSON.stringify(statusData, null, 2);
                    } else if (attempts >= maxAttempts) {
                        clearInterval(pollInterval);
                        statusOutput.textContent = '⏱️ Task is taking longer than expected. Check back soon.';
                    }
                } catch (error) {
                    console.error('Error polling status:', error);
                }
            }, 2000);
        } else {
            statusOutput.textContent = `❌ Error: ${data.error || 'Unknown error'} (Status: ${response.status})`;
        }
    } catch (error) {
        console.error('Error submitting task:', error);
        statusOutput.textContent = `❌ Error: ${error.message}`;
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = originalText;
    }
}
