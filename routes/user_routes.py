from flask import Blueprint, request, jsonify
from services.user_service import get_all_users, get_user_by_id, create_user

users_bp = Blueprint("users", __name__, url_prefix="/users")


# ------------------------------------------------------------------ #
#  Helper: unified JSON response builder                              #
# ------------------------------------------------------------------ #

def _ok(payload: dict, status: int = 200):
    return jsonify(payload), status


def _err(message, status: int = 400, errors=None):
    body = {"success": False, "error": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status


# ------------------------------------------------------------------ #
#  GET /users                                                         #
#  GET /users?search=<term>                                           #
#  GET /users?page=1&limit=10                                         #
# ------------------------------------------------------------------ #

@users_bp.route("", methods=["GET"])
def list_users():
    """
    Retrieve all users with optional search & pagination.

    Query params:
        search (str)  – filter by name or email (case-insensitive)
        page   (int)  – page number (default: 1)
        limit  (int)  – records per page (default: 10, max: 100)
    """
    search = request.args.get("search", "").strip() or None
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
    except (TypeError, ValueError):
        return _err("'page' and 'limit' must be integers.")

    if page < 1:
        return _err("'page' must be >= 1.")
    if limit < 1:
        return _err("'limit' must be >= 1.")

    result = get_all_users(search=search, page=page, limit=limit)
    return _ok(result)


# ------------------------------------------------------------------ #
#  POST /users                                                        #
# ------------------------------------------------------------------ #

@users_bp.route("", methods=["POST"])
def create_user_route():
    """
    Create a new user.

    Request body (JSON):
        {
            "name":  "John Doe",
            "email": "john@example.com",
            "role":  "user"
        }
    """
    payload = request.get_json(silent=True)
    if not payload:
        return _err("Request body must be valid JSON.", status=400)

    try:
        result = create_user(payload)
        return _ok(result, status=201)
    except ValueError as exc:
        msg = exc.args[0]
        # Validation errors come as a list; duplicate email as a plain string
        if isinstance(msg, list):
            return _err("Validation failed.", status=422, errors=msg)
        return _err(str(msg), status=409)
    except RuntimeError as exc:
        return _err(str(exc), status=500)


# ------------------------------------------------------------------ #
#  GET /users/<id>                                                    #
# ------------------------------------------------------------------ #

@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    """Retrieve a single user by their numeric ID."""
    try:
        result = get_user_by_id(user_id)
        return _ok(result)
    except ValueError as exc:
        return _err(str(exc), status=404)
    except Exception as exc:
        return _err(str(exc), status=500)
