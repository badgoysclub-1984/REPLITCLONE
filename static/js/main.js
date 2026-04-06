// REPLITCLONE Main Script

/* ── Settings panel ─────────────────────────────────────── */
function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    if (panel) panel.classList.toggle('hidden');
}

/* ── Gemini API key management ──────────────────────────── */
async function saveGeminiKey() {
    const keyInput = document.getElementById('gemini-api-key');
    const statusEl = document.getElementById('gemini-status');
    const apiKey = keyInput ? keyInput.value.trim() : '';

    if (!apiKey || apiKey.startsWith('•')) {
        setStatus(statusEl, 'Please enter a valid API key.', 'err');
        return;
    }

    try {
        const resp = await fetch('/settings/gemini', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey }),
        });
        const data = await resp.json();
        if (resp.ok) {
            setStatus(statusEl, '✅ ' + data.message, 'ok');
            updateGeminiStatus(true);
        } else {
            setStatus(statusEl, '❌ ' + (data.error || 'Failed to save key'), 'err');
        }
    } catch (e) {
        setStatus(statusEl, '❌ Network error: ' + e.message, 'err');
    }
}

async function removeGeminiKey() {
    const statusEl = document.getElementById('gemini-status');
    try {
        const resp = await fetch('/settings/gemini', { method: 'DELETE' });
        const data = await resp.json();
        if (resp.ok) {
            setStatus(statusEl, '✅ ' + data.message, 'ok');
            updateGeminiStatus(false);
        } else {
            setStatus(statusEl, '❌ ' + (data.error || 'Failed'), 'err');
        }
    } catch (e) {
        setStatus(statusEl, '❌ Network error: ' + e.message, 'err');
    }
}

/** Update the Gemini badge in the chat pane header without a page reload. */
function updateGeminiStatus(configured) {
    const badge = document.querySelector('.chat-pane .badge');
    if (!badge) return;
    if (configured) {
        badge.textContent = 'Ready';
        badge.className = 'badge badge-ok';
    } else {
        badge.textContent = 'API key needed';
        badge.className = 'badge badge-warn';
    }
}

function setStatus(el, msg, type) {
    if (!el) return;
    el.textContent = msg;
    el.className = 'status-msg ' + (type || '');
}

/* ── Code runner ────────────────────────────────────────── */
async function runCode() {
    const code = document.getElementById('code').value;
    const outputEl = document.getElementById('output');
    if (outputEl) outputEl.textContent = 'Running…';

    try {
        const resp = await fetch('/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
        });
        const data = await resp.json();
        if (outputEl) outputEl.textContent = data.output || data.error || '';
    } catch (e) {
        if (outputEl) outputEl.textContent = 'Error: ' + e.message;
    }
}

/* ── Gemini AI chat ─────────────────────────────────────── */
function appendMessage(text, role) {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    const div = document.createElement('div');
    div.className = 'chat-msg ' + role;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

async function sendChat() {
    const inputEl = document.getElementById('chat-input');
    const prompt = inputEl ? inputEl.value.trim() : '';
    if (!prompt) return;

    appendMessage(prompt, 'user');
    if (inputEl) inputEl.value = '';

    try {
        const resp = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt }),
        });
        const data = await resp.json();
        if (resp.ok) {
            appendMessage(data.response, 'ai');
        } else {
            appendMessage('Error: ' + (data.error || 'Unknown error'), 'err');
        }
    } catch (e) {
        appendMessage('Error: ' + e.message, 'err');
    }
}

function handleChatKey(event) {
    // Ctrl+Enter or Cmd+Enter to send
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        sendChat();
    }
}

/* ── Repository Link Key management ─────────────────────── */
async function generateRepoLinkKey() {
    const keyInput = document.getElementById('repo-link-key');
    const statusEl = document.getElementById('repo-key-status');

    try {
        const resp = await fetch('/api/repo-link-key', { method: 'POST' });
        const data = await resp.json();
        if (resp.ok) {
            if (keyInput) keyInput.value = data.key;
            setStatus(statusEl, '✅ Repository link key generated. Copy and store it safely — it won\'t be shown again.', 'ok');
        } else {
            setStatus(statusEl, '❌ ' + (data.error || 'Failed to generate key'), 'err');
        }
    } catch (e) {
        setStatus(statusEl, '❌ Network error: ' + e.message, 'err');
    }
}

async function revokeRepoLinkKey() {
    const keyInput = document.getElementById('repo-link-key');
    const statusEl = document.getElementById('repo-key-status');

    try {
        const resp = await fetch('/api/repo-link-key', { method: 'DELETE' });
        const data = await resp.json();
        if (resp.ok) {
            if (keyInput) {
                keyInput.value = '';
                keyInput.placeholder = 'Click Generate to create a key';
            }
            setStatus(statusEl, '✅ ' + data.message, 'ok');
        } else {
            setStatus(statusEl, '❌ ' + (data.error || 'Failed to revoke key'), 'err');
        }
    } catch (e) {
        setStatus(statusEl, '❌ Network error: ' + e.message, 'err');
    }
}
