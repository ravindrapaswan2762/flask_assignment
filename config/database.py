import mysql.connector
from mysql.connector import pooling, Error
from config.settings import get_config

config = get_config()

# Database connection pool configuration
_connection_pool = None


def _create_pool():
    """Create and return a MySQL connection pool."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pooling.MySQLConnectionPool(
            pool_name="flask_pool",
            pool_size=5,
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
        )
    return _connection_pool


def get_db_connection():
    """Get a connection from the pool."""
    pool = _create_pool()
    return pool.get_connection()


def init_db():
    """Initialize the database: create DB and table if not exists."""
    # First connect without a database to create it
    conn = mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )
    cursor = conn.cursor()

    # Create the database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}`")
    cursor.execute(f"USE `{config.DB_NAME}`")

    # Create the users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS `users` (
            `id`         INT          NOT NULL AUTO_INCREMENT,
            `name`       VARCHAR(255) NOT NULL,
            `email`      VARCHAR(255) NOT NULL UNIQUE,
            `role`       VARCHAR(100) NOT NULL,
            `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            `updated_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            INDEX `idx_email` (`email`),
            INDEX `idx_name`  (`name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[DB] Database '{config.DB_NAME}' and table 'users' are ready.")
