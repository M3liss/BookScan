import sqlite3

class BookDatabase:
    def __init__(self, path):
        self.path = path
        self.create_database()

    def _get_connection(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_database(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    genre TEXT,
                    favourite INTEGER DEFAULT 0,
                    image TEXT DEFAULT 'Not found',
                    read INTEGER DEFAULT 0,
                    currently_reading INTEGER DEFAULT 0
                    )''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            reading_goal INTEGER DEFAULT 20,
            sharing_enabled INTEGER DEFAULT 1,
            recommendations_enabled INTEGER DEFAULT 1,
            tailscale_enabled INTEGER DEFAULT 1
        )
        ''')
        c.execute('''
                INSERT OR IGNORE INTO settings
                    (id, reading_goal, sharing_enabled, recommendations_enabled, tailscale_enabled)
                    VALUES
                    (1,20,1,1,1)''')

        conn.commit()
        conn.close()

    def add_book(self, isbn, title, author, genre, favourite, read, current_read):
        conn = self._get_connection()
        try:
            c = conn.cursor()
            if self.book_exists(isbn, c):
                return {"success": False, "error": "Book already exists"}
            fav = 1 if favourite else 0
            read_flag = 1 if read else 0
            c.execute(
                'INSERT INTO books (isbn, title, author, genre, favourite, image, read) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (isbn, title, author, genre, fav, "Not found", read_flag)
            )
            conn.commit()
            print("Book added successfully")
            return {"success": True, "message": "Book added successfully"}
            
        except sqlite3.Error as e:
            print("SQLite error:", e)
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                conn.close()

    def book_exists(self, isbn, cursor):
        cursor.execute("SELECT 1 FROM books WHERE isbn=? LIMIT 1", (isbn,))
        return cursor.fetchone() is not None

    def del_book(self, book_id):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM books WHERE id=?', (book_id,))
        deleted = c.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def toggle_fav(self, book_id):
        conn = self._get_connection()
        """Toggle favourite status for a book"""
        c = conn.cursor()
        c.execute(
            "UPDATE books SET favourite = NOT favourite WHERE id = ?",
            (book_id,)
        )
        conn.commit()
        conn.close()

    def toggle_read(self, book_id):
        conn = self._get_connection()
        """Toggle read status for a book"""
        c = conn.cursor()
        c.execute(
            "UPDATE books SET read = NOT read WHERE id = ?",
            (book_id,)
        )
        conn.commit()
        conn.close()

    def get_all_books(self):
        """
        Returns a list of all books with their title, favourite status, and read status.
        Each book is a dictionary: {"title": str, "favourite": bool, "read": bool}
        """
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM books")
        rows = c.fetchall()
        conn.close()

        books = []
        for row in rows:

            books.append({
                "id": row["id"],
                "isbn": row["isbn"],
                "title": row["title"],
                "author": row["author"],
                "genre": row["genre"],
                "favourite": bool(row["favourite"]),
                "image": row["image"],
                "read": bool(row["read"])
            })

        return books
        
    def update_book_status(self, book_id, read=None, favourite=None):
        conn = self._get_connection()
        c = conn.cursor()
        if read is not None:
            read = 1 if read else 0
            c.execute(
                "UPDATE books SET read=? WHERE id=?",
                (read, book_id)
            )
        if favourite is not None:
            favourite = 1 if favourite else 0
            c.execute(
                "UPDATE books SET favourite=? WHERE id=?",
                (favourite, book_id)
            )
        conn.commit()
        conn.close()

    def get_read_ratio(self):
        """Get stats on the books in the database."""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM books WHERE read = 1')
        read = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM books')
        total_count = c.fetchone()[0]

        conn.close()

        if total_count > 0:
            ratio = read / total_count
            return ratio
        return 0
    
    def get_book(self, book_id):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute( "SELECT * FROM books WHERE id=?",(book_id,))
        row = c.fetchone()
        conn.close()
        if row is None:
            return None
        return dict(row)
    
    def edit_book(self, book_id, title, author):

        conn = self._get_connection()
        cursor = conn.execute(""" UPDATE books SET title=?, author=? WHERE id=?""",(title,author,book_id))

        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return {"success": False,"error": "Book not found"}
        
        return {"success": True}
        
    def search_books(self, query):
        conn = self._get_connection()
        c = conn.cursor()
        search = f"%{query}%"
        c.execute(""" SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?""",(search, search, search))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_book_by_isbn(self, isbn):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT * FROM books WHERE isbn=?",
            (isbn,)
        )
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def count_books(self):

        conn = self._get_connection()

        row = conn.execute(
            """
            SELECT COUNT(*) as count
            FROM books
            """
        ).fetchone()

        conn.close()

        return row["count"]

    def get_unread_books(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE read=0")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_read_count(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM books WHERE read=1"
        )
        count = c.fetchone()
        conn.close()
        return count
    
    def get_favourite_books(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT * FROM books WHERE favourite=1"
        )
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_total_count(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM books"
        )
        count = c.fetchone()[0]
        conn.close()
        return count
    def set_currently_reading(self, book_id):
        """Mark one book as currently reading; unsets any previous one."""
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("UPDATE books SET currently_reading=0")           # clear old
        c.execute("UPDATE books SET currently_reading=1 WHERE id=?", (book_id,))  # set new
        conn.commit()
        conn.close()

    def clear_currently_reading(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("UPDATE books SET currently_reading=0")
        conn.commit()
        conn.close()

    def get_currently_reading(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE currently_reading=1 LIMIT 1")
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_reading_goal(self):
        conn = self._get_connection()
        row = conn.execute("SELECT reading_goal FROM settings WHERE id=1").fetchone()
        rows = conn.execute(
        "SELECT * FROM settings"
        ).fetchall()

        for row in rows:
            print("helooo")
            print(dict(row))

        conn.close()
        conn.close()
        return row["reading_goal"] if row else 20

    def set_reading_goal(self, goal):
        conn = self._get_connection()
        conn.execute("UPDATE settings SET reading_goal=? WHERE id=1", (goal,))
        conn.commit()
        conn.close()

    def get_setting(self, setting):

        conn = self._get_connection()

        row = conn.execute(
            f"""
            SELECT {setting}
            FROM settings
            WHERE id=1
            """
        ).fetchone()

        conn.close()

        return row[setting] if row else None
    def set_setting(self, setting, value):
        allowed = [
            "reading_goal",
            "sharing_enabled",
            "recommendations_enabled",
            "tailscale_enabled"
        ]
        if setting not in allowed:
            raise ValueError(
                "Invalid setting"
            )
        conn = self._get_connection()
        conn.execute(
            f"""
            UPDATE settings
            SET {setting}=?
            WHERE id=1
            """,
            (value,)
        )


        conn.commit()
        conn.close()