"""Tests for the Flask server endpoints"""
import json
import os
import sys
import unittest

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('SECRET_KEY', 'test-secret-key')

from src.server.app import app  # noqa: E402


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


if __name__ == '__main__':
    unittest.main()
