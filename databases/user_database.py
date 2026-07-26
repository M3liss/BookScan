# user_database.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class UserDatabase:

    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "change_this_password"
    ROLE_USER = "user"
    ROLE_ADMIN = "admin"

    def __init__(self, path="users.db"):
        self.path = path
        self._create_table()
        self._create_default_admin()

    def _get_connection(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table(self):
        conn = self._get_connection()
        conn.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
                CHECK(role IN ('{self.ROLE_USER}', '{self.ROLE_ADMIN}'))
                DEFAULT '{self.ROLE_USER}',
            created_at DATETIME NOT NULL
                DEFAULT CURRENT_TIMESTAMP
            )
        """)        
        conn.commit()

    def _create_default_admin(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username=?",
            (self.ADMIN_USERNAME,)
        )
        if cursor.fetchone() is None:
            password_hash = generate_password_hash(self.ADMIN_PASSWORD)
            cursor.execute(
                """
                INSERT INTO users
                (username, password_hash, role)
                VALUES (?, ?, ?)
                """,
                (
                    self.ADMIN_USERNAME,
                    password_hash,
                    self.ROLE_ADMIN
                )
            )
            conn.commit()

    def _validate_username(self, username):
        username = username.strip()
        if not username:
            raise ValueError("Username cannot be empty.")
        if len(username) < 3:
            raise ValueError("Username too short.")
        if len(username) > 32:
            raise ValueError("Username too long.")
        return username
    
    def _validate_password(self, password):
        password = password.strip()
        if not password:
            raise ValueError("Password cannot be empty.")
        if len(password) < 8:
            raise ValueError("Password too short.")
        return password
    
    def add_user(self, username, password):
        username = self._validate_username(username)
        password = self._validate_password(password)
        conn = self._get_connection()
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, self.ROLE_USER)
            )
            conn.commit()
            return True # new username
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "UNIQUE constraint failed: users.username" in str(e):
                return False
            raise

    def verify_user(self, username, password):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row is None:
            return False

        return check_password_hash(
            row["password_hash"],
            password
        )

    def get_role(self, username):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        return row["role"] if row else None
        
    def close_database(self):
        conn = self._get_connection()
        conn.close()

    def change_password(self, username, new_password):
        new_hash = generate_password_hash(new_password)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET password_hash=?
            WHERE username=?
            """,
            (
                new_hash,
                username
            )
        )
        conn.commit()
        conn.close()

    def delete_user(self, username):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM users
            WHERE username=?
            """,
            (username,)
        )
        conn.commit()
        conn.close()

    