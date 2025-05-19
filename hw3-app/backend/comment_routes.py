# comment_routes.py
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

comment_bp = Blueprint('comment', __name__)

# Database connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://root:rootpassword@mongo:27017/mydatabase?authSource=admin")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
users_col = db["users"]
comments_col = db["comments"]

# Helper function: get user email from session
def get_logged_in_user():
    user_info = session.get("user")
    if not user_info or "email" not in user_info:
        raise RuntimeError("User not authenticated")
    return {
        "email": user_info["email"],
        "name": user_info.get("name", "")
    }

# GET all comments for an article
@comment_bp.route("/comments/<path:article_id>", methods=["GET"])
def get_comments(article_id):
    comment_list = list(comments_col.find({"article_id": article_id}))
    for comment in comment_list:
        comment["_id"] = str(comment["_id"])
    return jsonify(comment_list)


# POST a new comment
@comment_bp.route("/comments/<path:article_id>", methods=["POST"])
def post_comment(article_id):
    try:
        user = get_logged_in_user()
        data = request.get_json()

        if not data or "comment" not in data:
            return jsonify({"error": "Missing comment"}), 400

        # Handle parent_id safely (could be None)
        parent_id = data.get("parent_id")

        comment_doc = {
            "article_id": article_id,
            "user_email": user["email"],
            "user_name": user["name"],
            "comment": data["comment"],
            "timestamp": datetime.utcnow(),
            "parent_id": parent_id  # optional
        }

        comments_col.insert_one(comment_doc)
        return jsonify({"message": "Comment added"}), 201

    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

# PUT (edit) a comment
@comment_bp.route("/comments/<comment_id>", methods=["PUT"])
def update_comment(comment_id):
    user_email = get_logged_in_user()
    data = request.get_json()

    if not data or "comment" not in data:
        return jsonify({"error": "Missing comment text"}), 400

    result = comments_col.update_one(
        {"_id": ObjectId(comment_id), "user_email": user_email},
        {"$set": {"comment": data["comment"], "timestamp": datetime.now(datetime.UTC)}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Not found or not authorized"}), 404

    return jsonify({"message": "Comment updated"})

# DELETE a comment
@comment_bp.route("/comments/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    user = get_logged_in_user()

    if user["email"] != "moderator@hw3.com":
        return jsonify({"error": "Unauthorized"}), 403

    # Delete the comment itself
    result = comments_col.delete_one({"_id": ObjectId(comment_id)})

    # Recursively delete child comments
    def delete_children(parent_id):
        children = list(comments_col.find({"parent_id": parent_id}))
        for child in children:
            comments_col.delete_one({"_id": child["_id"]})
            delete_children(str(child["_id"]))  # recurse

    delete_children(comment_id)

    return jsonify({"message": "Comment and replies deleted"}), 200
