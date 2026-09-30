// ANOMYMOUS Dashboard Application
// Modern AI Task Execution Interface
// Browser-compatible HTML5/ES6 implementation

class AnomyMousDashboard {
    constructor() {
        this.state = {
            health: 'checking',
            providers: [],
            analytics: {},
            taskStatus: 'idle'
        };
        this.pollingInterval = null;
        this.pollingAttempts = 0;
        this.maxPollingAttempts = 30;
        this.pollingTimeout = 60000; 
        this.isSubmitting = false;
        this.capabilities = {};
        this.initialize();
    }

    async initialize() {
        this.setupEventListeners();
        await Promise.all([
            this.loadHealth(),
            this.loadProviders(),
            this.loadAnalytics(),
            this.loadCapabilities()
        ]);
        this.renderProviders();
        this.renderAnalytics();
        this.renderCapabilities();
        this.updateHealthIndicator();
        this.init();
    }

    init() {
        console.log('[AnomyMousDashboard] Init complete');
    }

    async loadHealth() {
        try {
            const res = await fetch('/health');
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const d = await res.json();
            this.state.health = d.status === 'ok' ? 'healthy' : 'degraded';
            this.updateHealthIndicator();
        } catch (e) {
            console.error('[Health] Error:', e.message);
            this.state.health = 'unhealthy';
            this.updateHealthIndicator();
        }
    }

    updateHealthIndicator() {
        const i = document.getElementById('healthIndicator');
        if (!i) return;
        const d = i.querySelector('.health-dot'), t = i.querySelector('.health-text');
        if (!d || !t) return;
        const m = { healthy: 'Healthy', degraded: 'Degraded', unhealthy: 'Unhealthy', checking: 'Checking...' };
        d.className = 'health-dot ' + (this.state.health || 'checking');
        t.textContent = m[this.state.health] || 'Checking...';
    }

    async loadCapabilities() {
        try {
            const r = await fetch('/capabilities');
            if (!r.ok) throw new Error('HTTP ' + r.status);
            const d = await r.json();
            this.capabilities = d.capabilities || {};
        } catch(e) { this.capabilities = {}; }
    }

    renderCapabilities() {
        const c = document.getElementById('capabilitiesGrid');
        if (!c) return;
        const list = this.capabilities.length ? this.capabilities : [
            {n: 'LLM Processing', e: true}, {n: 'Code Gen', e: false}, 
            {n: 'Files', e: true}, {n: 'Network', e: true}];
        c.innerHTML = list.map(x =>
            '<div class="cap-item ' + (x.e ? 'enabled' : 'disabled') + '">\n                <div class="cap-name">' + x.n + '</div>\n                <div class="cap-status">' + (x.e ? 'Enabled' : 'Disabled') + '</div></div>')
            .join('') || '<div class="cap-loading">Loading...</div>';
    }

    async loadProviders() {
        try {
            const r = await fetch('/providers');
            if (!r.ok) throw new Error('HTTP ' + r.status);
            const d = await r.json();
            this.state.providers = d.providers || [];
        } catch(e) { this.state.providers = []; }
    }

    renderProviders() {
        const c = document.getElementById('providersList');
        if (!c) return;
        if (!this.state.providers || !this.state.providers.length) {
            c.innerHTML = '<div class="loading">No providers available</div>';
            return;
        }
        c.innerHTML = this.state.providers.map(p => {
            const n = p.name, cfg = {groq: 'Groq', google: 'GoogleAI', cerebras: 'Cerebras', mistral: 'Mistral', openrouter: 'OpenRouter'}[n] || n;
            return '<div class="provider-card"><div class="provider-header">\n                <span class="provider-name">' + cfg + '</span><span class="provider-status unavailable">Requires Auth</span></div>\n                <div class="provider-details"><div class="provider-detail"><span class="provider-detail-label">Models:</span><span class="provider-detail-value">' + (p.model_count||0) + '</span></div>\n                <div class="provider-detail"><span class="provider-detail-label">Auth:</span><span class="provider-detail-value">' + (p.requires_auth?'required':'none') + '</span></div></div></div>';
        }).join('') || '<div class="loading">Loading...</div>';
    }

    async loadAnalytics() {
        try {
            const r = await fetch('/analytics');
            if (!r.ok) throw new Error('HTTP ' + r.status);
            this.state.analytics = await r.json();
        } catch(e) { this.state.analytics = {total_requests:0, success_rate:0}; }
    }

    renderAnalytics() {
        const c = document.getElementById('analyticsGrid');
        if (!c) return;
        const t = this.state.analytics.total_requests || 0;
        const r = this.state.analytics.success_rate || 0;
        const p = this.state.providers.length;
        c.innerHTML = `
            <div class="analytics-card"><div class="analytics-value">${t}</div><div class="analytics-label">Total Tasks</div></div>
            <div class="analytics-card"><div class="analytics-value">${(r*100).toFixed(1)}%</div><div class="analytics-label">Success Rate</div></div>
            <div class="analytics-card"><div class="analytics-value">${p}</div><div class="analytics-label">Providers</div></div>
        `;
    }

    submitTask() {
        if (this.isSubmitting) return;
        const inp = document.getElementById('taskInput');
        const out = document.getElementById('statusOutput');
        if (!inp || !out) return;
        const t = inp.value.trim();
        if (!t) {
            out.innerHTML = '<span class="error-message">Error: Task cannot be empty</span>';
            out.className = 'status-output error';
            return;
        }
        this.isSubmitting = true;
        this.state.taskStatus = 'submitting';
        out.className = 'status-output pending';
        out.innerHTML = '<span class="error-message">Submitting...</span>';
        this.performSubmission(inp, out);
    }

    async performSubmission(inp, out) {
        try {
            const r = await fetch('/task', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({task: inp.value}) });
            if (r.status >= 400) {
                let e = 'HTTP ' + r.status;
                try { const d = await r.json(); e += ': ' + (d.error || d.message || ''); } catch { e += ': ' + r.statusText; }
                throw new Error(e);
            }
            const d = await r.json();
            if (d.status !== 'accepted') throw new Error('Invalid: ' + d.status);
            out.innerHTML = '<span class="error-message">Task accepted... Polling...</span>';
            await this.pollStatus(out);
        } catch(e) {
            console.error('[Task] Error:', e);
            this.isSubmitting = false;
            this.state.taskStatus = 'failed';
            out.className = 'status-output error';
            out.innerHTML = '<span class="error-message">Error: ' + String(e) + '</span>';
        }
    }

    async pollStatus(out) {
        this.pollingAttempts = 0;
        const start = Date.now();
        clearInterval(this.pollingInterval);
        this.pollingInterval = setInterval(async () => {
            this.pollingAttempts++;
            if (Date.now() - start > 60000) {
                clearInterval(this.pollingInterval);
                this.isSubmitting = false;
                out.className = 'status-output error';
                out.innerHTML = '<span class="error-message">Task polling timed out</span>';
                return;
            }
            try {
                const r = await fetch('/status');
                if (!r.ok) throw new Error('HTTP ' + r.status);
                const d = await r.json();
                if (d.status === 'no_result') return;
                clearInterval(this.pollingInterval);
                this.isSubmitting = false;
                this.state.taskStatus = d.status;
                out.className = 'status-output ' + d.status;
                const outText = d.status === 'success' ? 'Success!' : 'Failed!';
                const outBody = d.output || d.result || d.execution || d.error || JSON.stringify(d);
                out.innerHTML = '<span class="error-message">' + outText + '</span><pre class="status-result">' + outBody + '</pre>';
            } catch(e) {
                clearInterval(this.pollingInterval);
                this.isSubmitting = false;
                this.state.taskStatus = 'failed';
                out.className = 'status-output error';
                out.innerHTML = '<span class="error-message">Polling error: ' + String(e) + '</span>';
            }
        }, 1000);
    }

    setupEventListeners() {
        const b = document.getElementById('runBtn');
        if (b) b.addEventListener('click', () => this.submitTask());
    }
}

if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new AnomyMousDashboard());
    } else { new AnomyMousDashboard(); }
}
