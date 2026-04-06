"""Web server for REPLITCLONE"""
import os
import secrets
import requests
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', '..', 'static'),
)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_API_USER_URL = 'https://api.github.com/user'


@app.route('/')
def home():
    """Render the main editor page."""
    return render_template('index.html',
                           github_user=session.get('github_user'),
                           gemini_configured=bool(session.get('gemini_api_key')),
                           repo_key_configured=bool(session.get('repo_link_key')))


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
# Repository Link Key
# ---------------------------------------------------------------------------

_REPO_KEY_PREFIX = 'rlk_'


@app.route('/api/repo-link-key', methods=['POST'])
def generate_repo_link_key():
    """Generate a new repository link key and store it in the session."""
    key = _REPO_KEY_PREFIX + secrets.token_hex(32)
    session['repo_link_key'] = key
    return jsonify({'status': 'ok', 'key': key})


@app.route('/api/repo-link-key', methods=['GET'])
def get_repo_link_key_status():
    """Return whether a repository link key is currently configured."""
    configured = bool(session.get('repo_link_key'))
    return jsonify({'configured': configured})


@app.route('/api/repo-link-key', methods=['DELETE'])
def revoke_repo_link_key():
    """Revoke (remove) the current repository link key from the session."""
    session.pop('repo_link_key', None)
    return jsonify({'status': 'ok', 'message': 'Repository link key revoked'})


if __name__ == "__main__":
    app.run(debug=True)

