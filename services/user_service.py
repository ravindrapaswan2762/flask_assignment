import re
from models.user_model import UserModel
from config.settings import get_config

config = get_config()

# Simple email regex – covers the vast majority of valid addresses
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9.\-]+$")

ALLOWED_ROLES = {"admin", "user", "moderator", "guest"}


# --------------------------------------------------------------------------- #
#  Validation helpers                                                          #
# --------------------------------------------------------------------------- #

def _validate_user_payload(name, email, role) -> list[str]:
    """Return a list of validation error messages (empty list = valid)."""
    errors = []

    # Required fields
    if not name or not str(name).strip():
        errors.append("'name' is required and cannot be blank.")
    if not email or not str(email).strip():
        errors.append("'email' is required and cannot be blank.")
    if not role or not str(role).strip():
        errors.append("'role' is required and cannot be blank.")

    # Email format
    if email and not _EMAIL_RE.match(str(email).strip()):
        errors.append(f"'{email}' is not a valid email address.")

    # Role whitelist (optional – comment out if you don't need it)
    # if role and str(role).strip().lower() not in ALLOWED_ROLES:
    #     errors.append(f"Role must be one of: {', '.join(sorted(ALLOWED_ROLES))}.")

    return errors


# --------------------------------------------------------------------------- #
#  Service functions                                                           #
# --------------------------------------------------------------------------- #

def get_all_users(search: str = None, page: int = 1, limit: int = 10) -> dict:
    """
    Retrieve users with optional search and pagination.

    Returns a dict with:
        success, data (list), pagination (meta), message
    """
    # Sanitise / clamp pagination params
    page = max(1, int(page))
    limit = max(1, min(int(limit), config.MAX_LIMIT))

    result = UserModel.get_all(search=search, page=page, limit=limit)

    return {
        "success": True,
        "data": result["users"],
        "pagination": {
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
        },
        "message": f"Retrieved {len(result['users'])} user(s).",
    }


def get_user_by_id(user_id: int) -> dict:
    """
    Retrieve a single user by ID.

    Returns a dict with: success, data, message
    Raises: ValueError if not found.
    """
    user_id = int(user_id)
    user = UserModel.get_by_id(user_id)
    if user is None:
        raise ValueError(f"User with ID {user_id} not found.")

    return {
        "success": True,
        "data": user,
        "message": "User retrieved successfully.",
    }


def create_user(payload: dict) -> dict:
    """
    Validate payload and create a new user.

    Returns a dict with: success, data, message
    Raises:
        ValueError  – validation errors or duplicate email
        RuntimeError – unexpected DB error
    """
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    role = str(payload.get("role", "")).strip()

    # Validation
    errors = _validate_user_payload(name, email, role)
    if errors:
        raise ValueError(errors)

    # Delegate to model (raises ValueError on duplicate email)
    new_user = UserModel.create(name=name, email=email, role=role)

    return {
        "success": True,
        "data": new_user,
        "message": "User created successfully.",
    }
