import tempfile
import unittest

from databases.database import BookDatabase
from services.sharing import SharingService


class TestSharingService(unittest.TestCase):
    def test_recommendations_require_installation_without_backend(self):
        service = SharingService()

        result = service.enable_recommendations(7)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "requires_installation")

    def test_build_public_profile_includes_book_stats(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db = BookDatabase(temp_dir, 1)
            db.add_book("123456", "Shared Book", "Alice", "Fiction", False, True, False)

            service = SharingService()
            profile = service.build_public_profile(1, db, username="alice")

            self.assertEqual(profile["username"], "alice")
            self.assertEqual(profile["book_count"], 1)
            self.assertEqual(profile["read_count"], 1)
            self.assertTrue(profile["sharing_enabled"])
