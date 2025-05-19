import unittest
from unittest.mock import patch, MagicMock
from app import app as flask_app
from flask import session
import json
import os

class MiscRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask_app.test_client()
        self.app.testing = True

    def test_api_key_route(self):
        os.environ["NYT_API_KEY"] = "fake-test-key"

        response = self.app.get("/api/key")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"apiKey": "fake-test-key"})

if __name__ == '__main__':
    unittest.main()
    
class AuthRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask_app.test_client()
        self.app.testing = True

    @patch("app.client")
    def test_login_redirect(self, mock_client):
        mock_client.authorize_redirect.return_value = flask_app.response_class(
            status=302,
            headers={"Location": "http://fake-auth-url"}
        )

        with self.app.session_transaction() as sess:
            sess["nonce"] = "abc123"

        response = self.app.get("/login")
        self.assertEqual(response.status_code, 302)
        self.assertIn("http://fake-auth-url", response.headers["Location"])

    @patch("app.client")
    def test_authorize_sets_user_session(self, mock_client):
        mock_token = {"id_token": "dummy"}
        mock_user_info = {
            "sub": "user123",
            "email": "testuser@example.com",
            "name": "Test User"
        }

        mock_client.authorize_access_token.return_value = mock_token
        mock_client.parse_id_token.return_value = mock_user_info

        with self.app.session_transaction() as sess:
            sess["nonce"] = "abc123"

        with patch("app.users_collection.update_one") as mock_update:
            response = self.app.get("/authorize", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")

        # Test if session is updated
        with self.app.session_transaction() as sess:
            self.assertEqual(sess["user"]["email"], "testuser@example.com")

    def test_logout_clears_session(self):
        with self.app.session_transaction() as sess:
            sess["user"] = {"email": "testuser@example.com"}
            sess["nonce"] = "abc123"

        response = self.app.get("/logout", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")

        # Ensure session is cleared
        with self.app.session_transaction() as sess:
            self.assertNotIn("user", sess)
            self.assertNotIn("nonce", sess)

    def test_me_returns_user_info(self):
        user_info = {
            "email": "testuser@example.com",
            "name": "Test User"
        }

        with self.app.session_transaction() as sess:
            sess["user"] = user_info

        response = self.app.get("/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), user_info)
if __name__ == '__main__':
    unittest.main()
