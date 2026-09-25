"""
Bonus: JWT Authentication middleware and routes.

Provides:
  POST /auth/login  - returns a JWT token
  GET  /auth/me     - returns the current logged-in user (requires token)

Usage:
  Add the Authorization header to protected requests:
    Authorization: Bearer <token>
"""

import jwt
import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from models.user_model import UserModel

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ------------------------------------------------------------------ #
#  JWT helpers                                                        #
# ------------------------------------------------------------------ #

def _generate_token(user: dict) -> str:
    """Generate a signed JWT for the given user dict."""
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"],
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def token_required(f):
    """
    Decorator that validates the JWT Bearer token.

    Attaches the decoded payload to `request.current_user`.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization header missing or malformed."}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "error": "Token has expired."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "error": "Invalid token."}), 401

        return f(*args, **kwargs)
    return decorated


# ------------------------------------------------------------------ #
#  Routes                                                             #
# ------------------------------------------------------------------ #

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user by email and return a JWT token.

    Request body (JSON):
        { "email": "john@example.com" }

    Note: This is a simplified login (no password) for demo purposes.
          In production, add password hashing (bcrypt/argon2).
    """
    payload = request.get_json(silent=True)
    if not payload or not payload.get("email"):
        return jsonify({"success": False, "error": "'email' is required."}), 400

    email = str(payload["email"]).strip().lower()

    # Look up user by email
    from config.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, role FROM users WHERE email = %s LIMIT 1", (email,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return jsonify({"success": False, "error": "No user found with that email."}), 404

    user = {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}
    token = _generate_token(user)

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": user,
    }), 200


@auth_bp.route("/me", methods=["GET"])
@token_required
def me():
    """
    Return the currently authenticated user.
    Requires a valid JWT Bearer token.
    """
    current = request.current_user
    user = UserModel.get_by_id(current["sub"])
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    return jsonify({"success": True, "data": user}), 200
