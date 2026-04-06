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

/* ── SSH Terminal ───────────────────────────────────────── */

let _term = null;
let _fitAddon = null;
let _socket = null;
let _sshConnected = false;

function _initTerminal() {
    if (_term) return;
    _term = new Terminal({
        theme: {
            background: '#0d0d0d',
            foreground: '#d4d4d4',
            cursor: '#a0c4ff',
        },
        fontFamily: '"Courier New", monospace',
        fontSize: 14,
        cursorBlink: true,
        scrollback: 5000,
    });
    _fitAddon = new FitAddon.FitAddon();
    _term.loadAddon(_fitAddon);
    _term.open(document.getElementById('terminal-container'));
    _fitAddon.fit();

    _term.onData(function (data) {
        if (_socket && _sshConnected) {
            _socket.emit('ssh_input', { data: data });
        }
    });

    window.addEventListener('resize', function () {
        if (_fitAddon) {
            _fitAddon.fit();
            if (_socket && _sshConnected && _term) {
                _socket.emit('ssh_resize', { cols: _term.cols, rows: _term.rows });
            }
        }
    });
}

function _initSocket() {
    if (_socket) return;
    _socket = io({ transports: ['websocket', 'polling'] });

    _socket.on('ssh_connected', function (data) {
        _sshConnected = true;
        _setSshBadge('Connected', 'badge-ok');
        _setActionBtn('Disconnect', 'btn-secondary', 'sshDisconnect()');
        setStatus(document.getElementById('ssh-connect-status'), '', '');
        closeSshModal();
        if (_term) _term.writeln('\r\n\x1b[32m✓ Connected to ' + data.username + '@' + data.host + '\x1b[0m\r\n');
    });

    _socket.on('ssh_output', function (data) {
        if (_term) _term.write(data.data);
    });

    _socket.on('ssh_error', function (data) {
        _sshConnected = false;
        const statusEl = document.getElementById('ssh-connect-status');
        setStatus(statusEl, '❌ ' + (data.message || 'Connection error'), 'err');
        if (_term) _term.writeln('\r\n\x1b[31m✗ ' + (data.message || 'Connection error') + '\x1b[0m\r\n');
    });

    _socket.on('ssh_disconnected', function (data) {
        _sshConnected = false;
        _setSshBadge('Disconnected', 'badge-warn');
        _setActionBtn('Connect', 'btn-primary', 'openSshModal()');
        if (_term) _term.writeln('\r\n\x1b[33m⚠ ' + (data.reason || 'Disconnected') + '\x1b[0m\r\n');
    });
}

function _setSshBadge(text, cls) {
    const badge = document.getElementById('ssh-status-badge');
    if (badge) { badge.textContent = text; badge.className = 'badge ' + cls; }
}

function _setActionBtn(text, cls, onclick) {
    const btn = document.getElementById('ssh-action-btn');
    if (btn) { btn.textContent = text; btn.className = 'btn btn-sm ' + cls; btn.setAttribute('onclick', onclick); }
}

function toggleTerminalPanel() {
    const panel = document.getElementById('terminal-panel');
    if (!panel) return;
    const isHidden = panel.classList.toggle('hidden');
    if (!isHidden) {
        _initTerminal();
        _initSocket();
        setTimeout(function () { if (_fitAddon) _fitAddon.fit(); }, 50);
    }
}

function openSshModal() {
    const modal = document.getElementById('ssh-modal');
    if (modal) modal.classList.remove('hidden');
    setStatus(document.getElementById('ssh-connect-status'), '', '');
}

function closeSshModal() {
    const modal = document.getElementById('ssh-modal');
    if (modal) modal.classList.add('hidden');
}

function sshConnect() {
    const host = (document.getElementById('ssh-host') || {}).value || '192.168.1.56';
    const portStr = (document.getElementById('ssh-port') || {}).value || '22';
    const username = (document.getElementById('ssh-username') || {}).value || '';
    const password = (document.getElementById('ssh-password') || {}).value || '';

    if (!username.trim()) {
        setStatus(document.getElementById('ssh-connect-status'), '❌ Username is required', 'err');
        return;
    }
    const port = parseInt(portStr, 10);
    if (isNaN(port) || port < 1 || port > 65535) {
        setStatus(document.getElementById('ssh-connect-status'), '❌ Port must be between 1 and 65535', 'err');
        return;
    }
    if (!host.trim()) {
        setStatus(document.getElementById('ssh-connect-status'), '❌ Host is required', 'err');
        return;
    }

    _initTerminal();
    _initSocket();

    const cols = _term ? _term.cols : 220;
    const rows = _term ? _term.rows : 50;

    setStatus(document.getElementById('ssh-connect-status'), 'Connecting…', '');
    _socket.emit('ssh_connect', { host: host.trim(), port: port, username: username.trim(), password: password, cols: cols, rows: rows });
}

function sshDisconnect() {
    if (_socket) _socket.emit('ssh_disconnect_request');
}

