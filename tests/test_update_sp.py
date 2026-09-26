import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add docs/.sphinx to path
SPHINX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", ".sphinx"))
if SPHINX_PATH not in sys.path:
    sys.path.insert(0, SPHINX_PATH)

import update_sp
update_sp.SPHINX_DIR = SPHINX_PATH


class TestUpdateSP(unittest.TestCase):

    def test_get_local_files_and_paths(self):
        local_files = update_sp.get_local_files_and_paths()
        self.assertIsInstance(local_files, dict)
        self.assertIn("update_sp.py", local_files)
        self.assertTrue(local_files["update_sp.py"].endswith("update_sp.py"))

    @patch("update_sp.download_file")
    @patch("update_sp.get_git_revision_hash")
    @patch("update_sp.query_api")
    def test_update_static_files_hashes_equal(self, mock_query_api, mock_get_hash, mock_download):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "name": "update_sp.py",
                "type": "file",
                "sha": "123456",
                "download_url": "http://example.com/update_sp.py",
            }
        ]
        mock_query_api.return_value = mock_response
        mock_get_hash.return_value = "123456"

        with patch("os.path.exists", return_value=False):
            files_updated, new_files = update_sp.update_static_files()
            self.assertFalse(files_updated)
            self.assertFalse(new_files)
            mock_download.assert_not_called()

    @patch("update_sp.download_file")
    @patch("update_sp.get_git_revision_hash")
    @patch("update_sp.query_api")
    def test_update_static_files_hash_different(self, mock_query_api, mock_get_hash, mock_download):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "name": "update_sp.py",
                "type": "file",
                "sha": "new_sha_123",
                "download_url": "http://example.com/update_sp.py",
            }
        ]
        mock_query_api.return_value = mock_response
        mock_get_hash.return_value = "old_sha_456"

        with patch("os.path.exists", return_value=True):
            files_updated, new_files = update_sp.update_static_files()
            self.assertTrue(files_updated)
            self.assertFalse(new_files)
            mock_download.assert_called_once()

    @patch("update_sp.download_file")
    @patch("update_sp.get_git_revision_hash")
    @patch("update_sp.query_api")
    def test_update_static_files_nested_dir(self, mock_query_api, mock_get_hash, mock_download):
        root_response = MagicMock()
        root_response.json.return_value = [
            {
                "name": "metrics",
                "type": "dir",
            }
        ]
        dir_response = MagicMock()
        dir_response.json.return_value = [
            {
                "name": "build_metrics.py",
                "type": "file",
                "sha": "dir_sha_789",
                "download_url": "http://example.com/build_metrics.py",
            }
        ]
        mock_query_api.side_effect = [root_response, dir_response]
        mock_get_hash.return_value = "dir_sha_789"

        with patch("os.path.exists", return_value=False):
            files_updated, new_files = update_sp.update_static_files()
            self.assertFalse(files_updated)
            self.assertFalse(new_files)
            mock_download.assert_not_called()


if __name__ == "__main__":
    unittest.main()
