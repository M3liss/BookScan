import os
import tempfile
from databases.user_database import UserDatabase
import unittest
from databases.database import BookDatabase


TEST_DB = "test_users.db"

class test_all(unittest.TestCase):
    def cleanup(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_admin_creation(self):
        self.cleanup()
        db = UserDatabase(TEST_DB)

        assert db.verify_user(
            "admin",
            "change_this_password"
        )

        assert db.get_role("admin") == db.ROLE_ADMIN

        db.close_database()
        self.cleanup()


    def test_user_creation(self):
        self.cleanup()
        db = UserDatabase(TEST_DB)

        result = db.add_user(
            "alice",
            "securepassword"
        )

        assert result is True

        assert db.verify_user(
            "alice",
            "securepassword"
        )

        assert db.get_role("alice") == db.ROLE_USER

        db.close_database()
        self.cleanup()


    def test_duplicate_username(self):
        self.cleanup()
        db = UserDatabase(TEST_DB)

        first = db.add_user(
            "bob",
            "password123"
        )

        second = db.add_user(
            "bob",
            "password123"
        )

        assert first is True
        assert second is False

        db.close_database()
        self.cleanup()


    def test_wrong_password(self):
        self.cleanup()
        db = UserDatabase(TEST_DB)

        db.add_user(
            "charlie",
            "correctpassword"
        )

        assert not db.verify_user(
            "charlie",
            "wrongpassword"
        )

        db.close_database()
        self.cleanup()


    def test_invalid_username(self):

        db = UserDatabase(TEST_DB)

        try:
            db.add_user(
                "",
                "password123"
            )

            assert False

        except ValueError:
            assert True

        db.close_database()
        self.cleanup()



class TestUserBooks(unittest.TestCase):

    def setUp(self):

        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

        self.db = BookDatabase(TEST_DB)


    def tearDown(self):

        self.db.conn.close() if hasattr(self.db, "conn") else None

        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)


    def create_test_book(self):

        result = self.db.add_book(
            "9780261103573",
            "The Hobbit",
            "J.R.R. Tolkien",
            "Fantasy",
            False,
            False
        )

        self.assertTrue(result["success"])

        return self.db.get_book_by_isbn(
            "9780261103573"
        )


    def test_database_creation(self):

        books = self.db.get_all_books()

        self.assertEqual(
            books,
            []
        )


    def test_add_book(self):

        result = self.db.add_book(
            "123456",
            "Test Book",
            "Author",
            "Fantasy",
            False,
            False
        )

        self.assertTrue(
            result["success"]
        )

        books = self.db.get_all_books()

        self.assertEqual(
            len(books),
            1
        )

        self.assertEqual(
            books[0]["title"],
            "Test Book"
        )


    def test_duplicate_isbn(self):

        self.db.add_book(
            "123456",
            "Book",
            "Author",
            "Fantasy",
            False,
            False
        )

        result = self.db.add_book(
            "123456",
            "Different Book",
            "Different Author",
            "Fantasy",
            False,
            False
        )

        self.assertFalse(
            result["success"]
        )


    def test_get_book_by_id(self):

        book = self.create_test_book()

        result = self.db.get_book(
            book["id"]
        )

        self.assertEqual(
            result["title"],
            "The Hobbit"
        )

    def test_get_setting_returns_none_for_missing_row(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db = BookDatabase(temp_dir, 1)
            self.assertIsNone(db.get_setting(999, "reading_goal"))


    def test_get_book_by_isbn(self):

        book = self.create_test_book()

        result = self.db.get_book_by_isbn(
            "9780261103573"
        )

        self.assertEqual(
            result["author"],
            "J.R.R. Tolkien"
        )


    def test_search_books(self):

        self.create_test_book()

        result = self.db.search_books(
            "Tolkien"
        )

        self.assertEqual(
            len(result),
            1
        )


    def test_delete_book(self):

        book = self.create_test_book()

        deleted = self.db.del_book(
            book["id"]
        )

        self.assertTrue(
            deleted
        )

        self.assertEqual(
            self.db.get_all_books(),
            []
        )


    def test_toggle_read(self):

        book = self.create_test_book()

        self.db.toggle_read(
            book["id"]
        )

        updated = self.db.get_book(
            book["id"]
        )

        self.assertEqual(
            updated["read"],
            1
        )


    def test_toggle_favourite(self):

        book = self.create_test_book()

        self.db.toggle_fav(
            book["id"]
        )

        updated = self.db.get_book(
            book["id"]
        )

        self.assertEqual(
            updated["favourite"],
            1
        )


    def test_update_book_status(self):

        book = self.create_test_book()

        self.db.update_book_status(
            book["id"],
            read=True,
            favourite=True
        )

        updated = self.db.get_book(
            book["id"]
        )

        self.assertEqual(
            updated["read"],
            1
        )

        self.assertEqual(
            updated["favourite"],
            1
        )


    def test_read_ratio(self):

        self.db.add_book(
            "1",
            "Read",
            "Author",
            "Genre",
            False,
            True
        )

        self.db.add_book(
            "2",
            "Unread",
            "Author",
            "Genre",
            False,
            False
        )

        ratio = self.db.get_read_ratio()

        self.assertEqual(
            ratio,
            0.5
        )


    def test_unread_books(self):

        self.db.add_book(
            "1",
            "Unread Book",
            "Author",
            "Genre",
            False,
            False
        )

        books = self.db.get_unread_books()

        self.assertEqual(
            len(books),
            1
        )

        self.assertEqual(
            books[0]["title"],
            "Unread Book"
        )