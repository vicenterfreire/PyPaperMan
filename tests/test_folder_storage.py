import json
import tempfile
import unittest
from pathlib import Path

from folder_storage import DEFAULT_INTERVAL, load_settings, save_settings


class SettingsStorageTests(unittest.TestCase):
    def test_missing_file_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                load_settings(Path(directory) / "folders.json"),
                ([], DEFAULT_INTERVAL),
            )

    def test_save_and_load_folders_and_interval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "folders.json"
            folders = [r"C:\wallpapers", r"D:\photos"]

            save_settings(folders, 900, file_path)

            self.assertEqual(
                load_settings(file_path),
                (folders, 900),
            )

    def test_legacy_folder_list_is_migrated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "folders.json"
            file_path.write_text(json.dumps(["C:\\wallpapers"]))

            self.assertEqual(
                load_settings(file_path),
                (["C:\\wallpapers"], DEFAULT_INTERVAL),
            )

    def test_invalid_saved_data_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "folders.json"
            file_path.write_text(
                json.dumps({"folders": ["C:\\wallpapers"], "interval": 0})
            )

            with self.assertRaises(ValueError):
                load_settings(file_path)

    def test_nonpositive_interval_cannot_be_saved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "folders.json"

            with self.assertRaises(ValueError):
                save_settings([], 0, file_path)


if __name__ == "__main__":
    unittest.main()
