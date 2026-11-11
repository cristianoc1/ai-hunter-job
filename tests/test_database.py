import os
import unittest
from unittest.mock import patch

from src.database.db import _get_supabase


class SupabaseConfigurationTests(unittest.TestCase):
    @patch.dict(
        os.environ,
        {"SUPABASE_URL": "not-a-url", "SUPABASE_KEY": "test-key"},
    )
    @patch("src.database.db._supabase", None)
    @patch("src.database.db.create_client")
    def test_rejects_invalid_url_before_creating_client(self, create_client) -> None:
        with self.assertRaisesRegex(RuntimeError, "SUPABASE_URL"):
            _get_supabase()
        create_client.assert_not_called()

    @patch.dict(
        os.environ,
        {"SUPABASE_URL": "https://project.supabase.co", "SUPABASE_KEY": ""},
    )
    @patch("src.database.db._supabase", None)
    @patch("src.database.db.create_client")
    def test_requires_supabase_key(self, create_client) -> None:
        with self.assertRaisesRegex(RuntimeError, "SUPABASE_KEY"):
            _get_supabase()
        create_client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
