"""Tests for the Flask server endpoints"""
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('SECRET_KEY', 'test-secret-key')

from src.server.app import app, socketio  # noqa: E402


class TestServerRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = app.test_client()

    # ------------------------------------------------------------------
    # Home
    # ------------------------------------------------------------------

    def test_home_returns_200(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'REPLITCLONE', resp.data)

    # ------------------------------------------------------------------
    # Settings – Gemini key
    # ------------------------------------------------------------------

    def test_save_gemini_key_success(self):
        resp = self.client.post(
            '/settings/gemini',
            data=json.dumps({'api_key': 'AIzaFakeKey123'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['status'], 'ok')

    def test_save_gemini_key_missing(self):
        resp = self.client.post(
            '/settings/gemini',
            data=json.dumps({'api_key': ''}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertIn('error', data)

    def test_remove_gemini_key(self):
        # First save a key
        self.client.post(
            '/settings/gemini',
            data=json.dumps({'api_key': 'AIzaFakeKey123'}),
            content_type='application/json',
        )
        # Then remove it
        resp = self.client.delete('/settings/gemini')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['status'], 'ok')

    # ------------------------------------------------------------------
    # AI chat – no key configured
    # ------------------------------------------------------------------

    def test_ai_chat_no_key_returns_401(self):
        resp = self.client.post(
            '/api/ai/chat',
            data=json.dumps({'prompt': 'Hello'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)
        data = json.loads(resp.data)
        self.assertIn('error', data)

    def test_ai_chat_empty_prompt_returns_400(self):
        # Save a key via the endpoint so the session contains it
        self.client.post(
            '/settings/gemini',
            data=json.dumps({'api_key': 'AIzaFakeKey'}),
            content_type='application/json',
        )
        resp = self.client.post(
            '/api/ai/chat',
            data=json.dumps({'prompt': ''}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # GitHub status – not linked
    # ------------------------------------------------------------------

    def test_github_status_not_linked(self):
        resp = self.client.get('/api/github/status')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertFalse(data['linked'])

    def test_github_status_linked(self):
        # Patch the session so it looks like GitHub is linked
        from unittest.mock import patch
        fake_user = {'login': 'octocat', 'name': 'The Octocat', 'avatar_url': ''}
        with patch('src.server.app.session', {'github_user': fake_user}):
            resp = self.client.get('/api/github/status')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data['linked'])
        self.assertEqual(data['user']['login'], 'octocat')

    # ------------------------------------------------------------------
    # GitHub auth redirect
    # ------------------------------------------------------------------

    def test_github_auth_no_client_id_returns_500(self):
        # When GITHUB_CLIENT_ID is not set the endpoint should return an error
        import src.server.app as server_module
        original = server_module.GITHUB_CLIENT_ID
        server_module.GITHUB_CLIENT_ID = ''
        try:
            resp = self.client.get('/auth/github')
            self.assertEqual(resp.status_code, 500)
        finally:
            server_module.GITHUB_CLIENT_ID = original

    # ------------------------------------------------------------------
    # Code runner
    # ------------------------------------------------------------------

    def test_run_code_prints_hello(self):
        resp = self.client.post(
            '/run',
            data=json.dumps({'code': 'print("hello world")'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn('hello world', data['output'])

    def test_run_code_syntax_error(self):
        resp = self.client.post(
            '/run',
            data=json.dumps({'code': 'def broken('}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn('Error', data['output'])


class TestSshTerminal(unittest.TestCase):
    """Tests for the SSH terminal Socket.IO events."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.socket_client = socketio.test_client(app)

    def tearDown(self):
        self.socket_client.disconnect()

    # ------------------------------------------------------------------
    # ssh_connect – missing username
    # ------------------------------------------------------------------

    def test_ssh_connect_no_username_emits_error(self):
        self.socket_client.emit('ssh_connect', {
            'host': '192.168.1.56',
            'port': 22,
            'username': '',
            'password': 'secret',
        })
        received = self.socket_client.get_received()
        events = [e['name'] for e in received]
        self.assertIn('ssh_error', events)
        error_evt = next(e for e in received if e['name'] == 'ssh_error')
        self.assertIn('Username', error_evt['args'][0]['message'])

    # ------------------------------------------------------------------
    # ssh_connect – connection refused (paramiko mocked)
    # ------------------------------------------------------------------

    def test_ssh_connect_failure_emits_error(self):
        with patch('paramiko.SSHClient') as MockSSHClient:
            mock_client = MagicMock()
            MockSSHClient.return_value = mock_client
            mock_client.connect.side_effect = Exception('Connection refused')

            self.socket_client.emit('ssh_connect', {
                'host': '192.168.1.56',
                'port': 22,
                'username': 'user',
                'password': 'wrong',
            })

        received = self.socket_client.get_received()
        events = [e['name'] for e in received]
        self.assertIn('ssh_error', events)

    # ------------------------------------------------------------------
    # ssh_connect – authentication failure (paramiko mocked)
    # ------------------------------------------------------------------

    def test_ssh_connect_auth_failure_emits_error(self):
        import paramiko
        with patch('paramiko.SSHClient') as MockSSHClient:
            mock_client = MagicMock()
            MockSSHClient.return_value = mock_client
            mock_client.connect.side_effect = paramiko.AuthenticationException()

            self.socket_client.emit('ssh_connect', {
                'host': '192.168.1.56',
                'port': 22,
                'username': 'user',
                'password': 'badpassword',
            })

        received = self.socket_client.get_received()
        events = [e['name'] for e in received]
        self.assertIn('ssh_error', events)
        error_evt = next(e for e in received if e['name'] == 'ssh_error')
        self.assertIn('Authentication', error_evt['args'][0]['message'])

    # ------------------------------------------------------------------
    # ssh_connect – success path (paramiko mocked)
    # ------------------------------------------------------------------

    def test_ssh_connect_success_emits_connected(self):
        with patch('paramiko.SSHClient') as MockSSHClient:
            mock_client = MagicMock()
            MockSSHClient.return_value = mock_client
            mock_channel = MagicMock()
            mock_channel.closed = False
            mock_channel.recv_ready.return_value = False
            mock_channel.recv_stderr_ready.return_value = False
            mock_client.invoke_shell.return_value = mock_channel

            self.socket_client.emit('ssh_connect', {
                'host': '192.168.1.56',
                'port': 22,
                'username': 'admin',
                'password': 'pass',
            })

        received = self.socket_client.get_received()
        events = [e['name'] for e in received]
        self.assertIn('ssh_connected', events)
        connected_evt = next(e for e in received if e['name'] == 'ssh_connected')
        self.assertEqual(connected_evt['args'][0]['host'], '192.168.1.56')
        self.assertEqual(connected_evt['args'][0]['username'], 'admin')

    # ------------------------------------------------------------------
    # ssh_disconnect_request – with no active session (should not crash)
    # ------------------------------------------------------------------

    def test_ssh_disconnect_request_no_session(self):
        self.socket_client.emit('ssh_disconnect_request', {})
        received = self.socket_client.get_received()
        events = [e['name'] for e in received]
        self.assertIn('ssh_disconnected', events)


if __name__ == '__main__':
    unittest.main()
