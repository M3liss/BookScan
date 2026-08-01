# user_database.py
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from databases.database import BookDatabase

DATABASEFOLDER = "databases"

class UserDatabase:

    ROLE_USER = "user"
    ROLE_ADMIN = "admin"

    def __init__(self, path=f"{DATABASEFOLDER}/users.db"):
        if path is None:
            path = os.path.join(DATABASEFOLDER, "users.db")
        self.path = path
        self._create_table()

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
        conn.close()

    def promote_user(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
                "UPDATE users SET role=? WHERE id=?",
                (self.ROLE_ADMIN, user_id)
            )
        conn.commit()
        conn.close()

    def _validate_username(self, username):
        username = username.strip().lower()
        if not username:
            raise ValueError("Username cannot be empty.")
        if len(username) < 3:
            raise ValueError("Username too short.")
        if len(username) > 32:
            raise ValueError("Username too long.")
        return username
    
    def _validate_password(self, password):
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
            conn.close()
            BookDatabase(DATABASEFOLDER, cursor.lastrowid)
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            conn.rollback()
            conn.close()
            if "UNIQUE constraint failed: users.username" in str(e):
                return False
            raise

    def verify_user(self, user_id, password):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row is None:
            return False

        return check_password_hash(
            row["password_hash"],
            password
        )

    def login_user(self, username, password):
        username = self._validate_username(username)
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        if row is None:
            return False
        if check_password_hash(row["password_hash"], password):
            return True
        return False

    def get_role(self, user_id):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        return row["role"] if row else None
        
    def close_database(self):
        conn = self._get_connection()
        conn.close()

    def change_password(self, user_id, password, new_password):
        if not self.verify_user(user_id, password):
            return False
        new_password = self._validate_password(new_password)
        new_hash = generate_password_hash(new_password)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET password_hash=?
            WHERE id=?
            """,
            (
                new_hash,
                user_id, 
            )
        )
        conn.commit()
        conn.close()
        return True

    def change_username(self, user_id, new_username):
        new_username = self._validate_username(new_username)
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE users SET username=? WHERE id=?""", (new_username, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError as e:
            conn.rollback()
            conn.close()
            if "UNIQUE constraint failed: users.username" in str(e):
                return False
            raise

    def delete_user(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM users WHERE id=?""",(user_id,))
        conn.commit()
        conn.close()
        deleted = cursor.rowcount > 0
        if deleted:
            book_path = os.path.join(DATABASEFOLDER, f"account_{user_id}.db")
            if os.path.exists(book_path):
                os.remove(book_path)
        return deleted

    def get_user_id(self, username):
        conn = self._get_connection()
        cursor = conn.cursor()
        username = self._validate_username(username)
        cursor.execute("""SELECT id FROM users WHERE username=?""", (username,))
        row = cursor.fetchone()
        conn.close()
        return row["id"] if row else None