import unittest
from unittest.mock import patch, MagicMock
from app import app as flask_app
from flask import session
import json
import os

# test the routes (Ex: /api/key)
class MiscRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask_app.test_client()
        self.app.testing = True

    def test_api_key_route(self):
        os.environ["NYT_API_KEY"] = "fake-test-key"
        # call the /api/key route
        response = self.app.get("/api/key")
        # check the response returns the correct key
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"apiKey": "fake-test-key"})

if __name__ == '__main__':
    unittest.main()

# teses the login, authorize, logout session    
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

    # test the authorize sets session after login
    @patch("app.client")
    def test_authorize_sets_user_session(self, mock_client):
        mock_token = {"id_token": "dummy"}
        mock_user_info = {
            "sub": "user123",
            "email": "testuser@example.com",
            "name": "Test User"
        }
        # make fale token
        mock_client.authorize_access_token.return_value = mock_token
        mock_client.parse_id_token.return_value = mock_user_info

        with self.app.session_transaction() as sess:
            sess["nonce"] = "abc123"
        
        # patch DB update
        with patch("app.users_collection.update_one") as mock_update:
            response = self.app.get("/authorize", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")

        # test if session is updated
        with self.app.session_transaction() as sess:
            self.assertEqual(sess["user"]["email"], "testuser@example.com")

    # test the logout seetion
    def test_logout_clears_session(self):
        with self.app.session_transaction() as sess:
            sess["user"] = {"email": "testuser@example.com"}
            sess["nonce"] = "abc123"

        response = self.app.get("/logout", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")

        # ensure session is cleared
        with self.app.session_transaction() as sess:
            self.assertNotIn("user", sess)
            self.assertNotIn("nonce", sess)

    # test return a current user
    def test_me_returns_user_info(self):
        user_info = {
            "email": "testuser@example.com",
            "name": "Test User"
        }
        # put user info in session
        with self.app.session_transaction() as sess:
            sess["user"] = user_info

        response = self.app.get("/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), user_info)
if __name__ == '__main__':
    unittest.main()
