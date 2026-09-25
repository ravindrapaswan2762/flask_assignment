from config.database import get_db_connection
from mysql.connector import Error


class UserModel:
    """
    Data-access layer for the 'users' table.
    All methods return plain dicts so the service layer stays DB-agnostic.
    """

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _row_to_dict(cursor, row) -> dict:
        """Convert a database row to a dictionary using column names."""
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        result = {}
        for col, val in zip(columns, row):
            # Convert datetime objects to ISO 8601 strings
            if hasattr(val, "isoformat"):
                result[col] = val.isoformat()
            else:
                result[col] = val
        return result

    # ------------------------------------------------------------------ #
    #  Read operations                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_all(search: str = None, page: int = 1, limit: int = 10) -> dict:
        """
        Return paginated users, optionally filtered by name/email.

        Returns:
            {
                "users": [...],
                "total": <int>,
                "page": <int>,
                "limit": <int>,
                "pages": <int>,
            }
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        offset = (page - 1) * limit

        if search:
            pattern = f"%{search}%"
            count_sql = "SELECT COUNT(*) FROM users WHERE name LIKE %s OR email LIKE %s"
            cursor.execute(count_sql, (pattern, pattern))
            total = cursor.fetchone()[0]

            data_sql = (
                "SELECT id, name, email, role, created_at, updated_at "
                "FROM users WHERE name LIKE %s OR email LIKE %s "
                "ORDER BY id ASC LIMIT %s OFFSET %s"
            )
            cursor.execute(data_sql, (pattern, pattern, limit, offset))
        else:
            cursor.execute("SELECT COUNT(*) FROM users")
            total = cursor.fetchone()[0]

            data_sql = (
                "SELECT id, name, email, role, created_at, updated_at "
                "FROM users ORDER BY id ASC LIMIT %s OFFSET %s"
            )
            cursor.execute(data_sql, (limit, offset))

        rows = cursor.fetchall()
        users = [UserModel._row_to_dict(cursor, row) for row in rows]

        cursor.close()
        conn.close()

        import math

        return {
            "users": users,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": math.ceil(total / limit) if total > 0 else 0,
        }

    @staticmethod
    def get_by_id(user_id: int) -> dict:
        """Return a single user dict or None if not found."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, role, created_at, updated_at FROM users WHERE id = %s",
            (user_id,),
        )
        row = cursor.fetchone()
        user = UserModel._row_to_dict(cursor, row)
        cursor.close()
        conn.close()
        return user

    @staticmethod
    def email_exists(email: str) -> bool:
        """Check whether an email address is already registered."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = %s LIMIT 1", (email,))
        exists = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return exists

    # ------------------------------------------------------------------ #
    #  Write operations                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def create(name: str, email: str, role: str) -> dict:
        """
        Insert a new user and return the created record.

        Raises:
            ValueError: if the email already exists.
            RuntimeError: on any other DB error.
        """
        if UserModel.email_exists(email):
            raise ValueError(f"Email '{email}' is already registered.")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, role) VALUES (%s, %s, %s)",
                (name, email, role),
            )
            conn.commit()
            new_id = cursor.lastrowid
        except Error as exc:
            conn.rollback()
            raise RuntimeError(f"Database error: {exc}") from exc
        finally:
            cursor.close()
            conn.close()

        return UserModel.get_by_id(new_id)
