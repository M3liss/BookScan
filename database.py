import sqlite3

class BookDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_database()

    def create_database(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS books
                  (id INTEGER PRIMARY KEY, 
                  isbn INT,
                  title TEXT, 
                  author TEXT, 
                  genre TEXT,
                  favourite BOOLEAN,
                  image TEXT,
                  read BOOLEAN)''')
        conn.commit()
        conn.close()

    def add_book(self, isbn, title, author, genre, favourite, read):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if self.book_exists(title):
            print("Book already exists")
        else:
            c.execute('INSERT INTO books (isbn, title, author, genre, favourite, image, read) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                    (isbn, title, author, genre, favourite, "Not found", read))
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

    def get_ratio(self):
        """Get stats on the books in the database."""
        conn = sqlite3.connect(self.db_name)
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
        
if __name__ == "main":
    user_db = BookDatabase('user1.db')

    #isbn, title, author, genre, favourite, read
    user_db.add_book('1', 'The Catcher in the Rye', 'J.D. Salinger', 'Fiction', False, True)
    user_db.add_book('1', 'The Hobbit', 'J.R.R. Tolkien', 'Fiction', False, False)
    print(user_db.get_ratio())
    #print(books)  # Should not include 'The Catcher in the Rye' anymore
    # Now delete the book by title
    #user_db.del_book("The Catcher in the Rye")

    # Verify deletion
    books = user_db.get_all_books()
    print(books)  # Should not include 'The Catcher in the Rye' anymore
