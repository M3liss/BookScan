import sqlite3
import openlibrary
from lookup import search_isbn

class BookDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_database()

    def create_database(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS books
                  (id INTEGER PRIMARY KEY, 
                  ISBN INT,
                  title TEXT, 
                  author TEXT, 
                  genre TEXT, 
                  scanned BOOLEAN,
                  read BOOLEAN)''')
        conn.commit()
        conn.close()

    def add_book(self, title, author, genre):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if self.book_exists(title):
            print("Book already exists")
        else:
            c.execute('INSERT INTO books (title, author, genre, scanned, read) VALUES (?, ?, ?, ?, ?)', 
                    (title, author, genre, False, False))
        conn.commit()
        conn.close()

    def book_exists(self, title):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM books WHERE title = ?', (title,))
        result = c.fetchone()
        conn.close()
        return result[0] > 0

    def del_book(self, title):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('DELETE FROM books WHERE title = ?', (title,))
        conn.commit()
        conn.close()

    def get_all_books(self):
        """Retrieve all books from the database."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT * FROM books')
        books = c.fetchall()
        conn.close()
        return books

    def update_book_status(self, book_id, scanned=None, read=None):
        """Update the scanned or read status of a book."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if scanned is not None:
            c.execute('UPDATE books SET scanned = ? WHERE id = ?', (scanned, book_id))
        if read is not None:
            c.execute('UPDATE books SET read = ? WHERE id = ?', (read, book_id))
        conn.commit()
        conn.close()

    def get_book_stats(self):
        """Get stats on the books in the database."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM books WHERE scanned = 1')
        scanned_count = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM books')
        total_count = c.fetchone()[0]

        conn.close()

        if total_count > 0:
            ratio = scanned_count / total_count
            return scanned_count, total_count, ratio
        else:
            return 0, 0, 0
        
    def lookup_book(self, title=None, author=None, isbn=None):
        """Search for a book by title, author, or ISBN using the Open Library API"""
        if isbn:
            # Search by ISBN
            result = search_isbn(str(isbn))
        elif author:
            result = 1
        elif title:
            result = 1        
        else:
            return None

        return result
        
user_db = BookDatabase('user1.db')

#user_db.add_book('The Catcher in the Rye', 'J.D. Salinger', 'Fiction')

#books = user_db.get_all_books()
#print(books)  # Should not include 'The Catcher in the Rye' anymore
# Now delete the book by title
#user_db.del_book("The Catcher in the Rye")

# Verify deletion
#books = user_db.get_all_books()
#print(books)  # Should not include 'The Catcher in the Rye' anymore

res = user_db.lookup_book(isbn = 9781526610140)
print(res)