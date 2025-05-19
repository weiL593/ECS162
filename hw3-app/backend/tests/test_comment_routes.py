import unittest
from unittest.mock import patch
from app import app as flask_app
from bson.objectid import ObjectId
import json

class CommentRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask_app.test_client()
        self.app.testing = True
        self.article_id = "nyt://test-article"

        # Simulate a logged-in user
        self.user = {
            "email": "testuser@example.com",
            "name": "Test User"
        }

    @patch("comment_routes.comments_col.find")
    def test_get_comments(self, mock_find):
        mock_find.return_value = [
            {
                "_id": ObjectId("60d5f3c4b4d9f1e5f8a3c1a1"),
                "article_id": self.article_id,
                "comment": "Sample Comment",
                "user_email": self.user["email"],
                "user_name": self.user["name"],
                "timestamp": "2024-01-01T00:00:00Z"
            }
        ]

        response = self.app.get(f"/comments/{self.article_id}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["comment"], "Sample Comment")

    @patch("comment_routes.comments_col.insert_one")
    @patch("comment_routes.session", {"user": {"email": "testuser@example.com", "name": "Test User"}})
    def test_post_comment_success(self, mock_insert):
        payload = {
            "comment": "This is a test comment.",
            "parent_id": None
        }

        response = self.app.post(
            f"/comments/{self.article_id}",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["message"], "Comment added")

    @patch("comment_routes.session", {"user": {"email": "moderator@hw3.com", "name": "Mod"}})
    @patch("comment_routes.comments_col.delete_one")
    @patch("comment_routes.comments_col.find")
    def test_delete_comment_with_replies(self, mock_find, mock_delete):
        comment_id = "60d5f3c4b4d9f1e5f8a3c1a1"

        # Simulate child comments
        mock_find.side_effect = [[
            {"_id": ObjectId("60d5f3c4b4d9f1e5f8a3c1a2"), "parent_id": comment_id}
        ], []]

        response = self.app.delete(f"/comments/{comment_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Comment and replies deleted")

if __name__ == '__main__':
    unittest.main()
