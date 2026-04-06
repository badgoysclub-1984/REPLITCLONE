"""Web server for REPLITCLONE"""
import os
import secrets
import threading
import requests
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from flask_socketio import SocketIO, emit, disconnect
from dotenv import load_dotenv

load_dotenv()

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', '..', 'static'),
)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_API_USER_URL = 'https://api.github.com/user'

# Active SSH sessions keyed by Socket.IO session id
_ssh_sessions: dict = {}
_ssh_sessions_lock = threading.Lock()


@app.route('/')
def home():
    """Render the main editor page."""
    return render_template('index.html',
                           github_user=session.get('github_user'),
                           gemini_configured=bool(session.get('gemini_api_key')))


@app.route('/run', methods=['POST'])
def run_code():
    """Execute submitted code and return output."""
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    output_lines = []
    try:
        import io
        import sys
        buf = io.StringIO()
        sys.stdout = buf
        exec(code, {})  # noqa: S102
        sys.stdout = sys.__stdout__
        output_lines = buf.getvalue()
    except Exception as exc:
        sys.stdout = sys.__stdout__
        output_lines = f'Error: {exc}'
    return jsonify({'output': output_lines})


# ---------------------------------------------------------------------------
# Settings – Gemini API key
# ---------------------------------------------------------------------------

@app.route('/settings/gemini', methods=['POST'])
def save_gemini_key():
    """Store the Gemini API key in the server-side session."""
    data = request.get_json(silent=True) or {}
    api_key = data.get('api_key', '').strip()
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    session['gemini_api_key'] = api_key
    return jsonify({'status': 'ok', 'message': 'Gemini API key saved successfully'})


@app.route('/settings/gemini', methods=['DELETE'])
def remove_gemini_key():
    """Remove the Gemini API key from the session."""
    session.pop('gemini_api_key', None)
    return jsonify({'status': 'ok', 'message': 'Gemini API key removed'})


# ---------------------------------------------------------------------------
# Gemini AI chat
# ---------------------------------------------------------------------------

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """Send a prompt to Gemini and return the response."""
    api_key = session.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return jsonify({'error': 'Gemini API key not configured. Add it in Settings.'}), 401

    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ---------------------------------------------------------------------------
# GitHub OAuth
# ---------------------------------------------------------------------------

@app.route('/auth/github')
def github_auth():
    """Redirect the user to GitHub to authorize the OAuth app."""
    if not GITHUB_CLIENT_ID:
        return jsonify({'error': 'GITHUB_CLIENT_ID is not configured on the server'}), 500
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'scope': 'read:user repo',
        'state': state,
    }
    query = '&'.join(f'{k}={v}' for k, v in params.items())
    return redirect(f'{GITHUB_AUTHORIZE_URL}?{query}')


@app.route('/auth/github/callback')
def github_callback():
    """Handle the GitHub OAuth callback."""
    error = request.args.get('error')
    if error:
        return redirect(url_for('home', error=error))

    code = request.args.get('code')
    state = request.args.get('state')
    if not code or state != session.pop('oauth_state', None):
        return redirect(url_for('home', error='invalid_state'))

    # Exchange code for access token
    token_resp = requests.post(
        GITHUB_TOKEN_URL,
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
        },
        headers={'Accept': 'application/json'},
        timeout=10,
    )
    token_data = token_resp.json()
    access_token = token_data.get('access_token')
    if not access_token:
        return redirect(url_for('home', error='token_exchange_failed'))

    # Fetch the authenticated user's profile
    user_resp = requests.get(
        GITHUB_API_USER_URL,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        },
        timeout=10,
    )
    user_data = user_resp.json()
    session['github_token'] = access_token
    session['github_user'] = {
        'login': user_data.get('login'),
        'name': user_data.get('name'),
        'avatar_url': user_data.get('avatar_url'),
    }
    return redirect(url_for('home'))


@app.route('/auth/github/logout')
def github_logout():
    """Disconnect the linked GitHub account."""
    session.pop('github_token', None)
    session.pop('github_user', None)
    return redirect(url_for('home'))


@app.route('/api/github/status')
def github_status():
    """Return whether a GitHub account is currently linked."""
    user = session.get('github_user')
    if user:
        return jsonify({'linked': True, 'user': user})
    return jsonify({'linked': False})


# ---------------------------------------------------------------------------
# SSH Terminal – Socket.IO events
# ---------------------------------------------------------------------------

def _ssh_reader(sid, channel):
    """Background thread: read SSH channel output and forward to the client."""
    try:
        while True:
            if channel.closed:
                break
            if channel.recv_ready():
                data = channel.recv(4096)
                if not data:
                    break
                socketio.emit('ssh_output', {'data': data.decode('utf-8', errors='replace')},
                              to=sid)
            if channel.recv_stderr_ready():
                data = channel.recv_stderr(4096)
                if data:
                    socketio.emit('ssh_output', {'data': data.decode('utf-8', errors='replace')},
                                  to=sid)
            socketio.sleep(0.05)
    except Exception:
        pass
    finally:
        socketio.emit('ssh_disconnected', {'reason': 'Channel closed'}, to=sid)
        _cleanup_ssh_session(sid)


def _cleanup_ssh_session(sid):
    """Close and remove an SSH session."""
    with _ssh_sessions_lock:
        entry = _ssh_sessions.pop(sid, None)
    if entry:
        try:
            entry['channel'].close()
        except Exception:
            pass
        try:
            entry['client'].close()
        except Exception:
            pass


@socketio.on('ssh_connect')
def handle_ssh_connect(data):
    """Open an SSH connection and start an interactive shell."""
    import paramiko

    sid = request.sid  # type: ignore[attr-defined]
    host = data.get('host', '192.168.1.56').strip()
    port_raw = data.get('port', 22)
    username = data.get('username', '').strip()
    password = data.get('password', '')
    cols = int(data.get('cols', 220))
    rows = int(data.get('rows', 50))

    if not username:
        emit('ssh_error', {'message': 'Username is required'})
        return

    try:
        port = int(port_raw)
        if not 1 <= port <= 65535:
            raise ValueError
    except (ValueError, TypeError):
        emit('ssh_error', {'message': 'Port must be an integer between 1 and 65535'})
        return

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    try:
        client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    except (FileNotFoundError, OSError):
        pass
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=10,
            allow_agent=False,
            look_for_keys=False,
        )
    except paramiko.AuthenticationException:
        emit('ssh_error', {'message': 'Authentication failed – check username / password'})
        client.close()
        return
    except paramiko.SSHException as exc:
        emit('ssh_error', {'message': f'SSH error: {exc}'})
        client.close()
        return
    except Exception as exc:
        msg = str(exc)
        if 'not found in known_hosts' in msg or 'Server' in msg:
            msg = (f'Host key for {host} not found in known_hosts. '
                   'Add the host key via ssh-keyscan or connect manually first.')
        emit('ssh_error', {'message': f'Connection failed: {msg}'})
        client.close()
        return

    channel = client.invoke_shell(term='xterm-256color', width=cols, height=rows)
    channel.setblocking(False)

    with _ssh_sessions_lock:
        _ssh_sessions[sid] = {'client': client, 'channel': channel}

    emit('ssh_connected', {'host': host, 'username': username})

    reader = threading.Thread(target=_ssh_reader, args=(sid, channel), daemon=True)
    reader.start()


@socketio.on('ssh_input')
def handle_ssh_input(data):
    """Forward keystrokes from the browser to the SSH channel."""
    sid = request.sid  # type: ignore[attr-defined]
    with _ssh_sessions_lock:
        entry = _ssh_sessions.get(sid)
    if entry:
        try:
            entry['channel'].send(data.get('data', ''))
        except Exception:
            pass


@socketio.on('ssh_resize')
def handle_ssh_resize(data):
    """Resize the remote PTY when the xterm.js terminal is resized."""
    sid = request.sid  # type: ignore[attr-defined]
    with _ssh_sessions_lock:
        entry = _ssh_sessions.get(sid)
    if entry:
        try:
            entry['channel'].resize_pty(width=int(data.get('cols', 80)),
                                        height=int(data.get('rows', 24)))
        except Exception:
            pass


@socketio.on('ssh_disconnect_request')
def handle_ssh_disconnect_request(data=None):
    """Close the active SSH session on request."""
    sid = request.sid  # type: ignore[attr-defined]
    _cleanup_ssh_session(sid)
    emit('ssh_disconnected', {'reason': 'Disconnected by user'})


@socketio.on('disconnect')
def handle_disconnect():
    """Clean up SSH sessions when a Socket.IO client disconnects."""
    sid = request.sid  # type: ignore[attr-defined]
    _cleanup_ssh_session(sid)


if __name__ == "__main__":
    socketio.run(app, debug=True)

