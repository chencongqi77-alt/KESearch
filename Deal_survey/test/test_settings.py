import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from deal_survey import settings


class ServiceSettingsTests(unittest.TestCase):
    def test_copy_only_approved_settings_and_preserve_existing_file(self):
        with TemporaryDirectory() as temp:
            directory = Path(temp) / "reader"
            directory.mkdir()
            private = directory / ".env.local"
            with (patch.object(settings, "DIRECTORY", directory),
                  patch.object(settings, "PRIVATE_ENV", private),
                  patch.object(settings, "_user_environment", return_value={"KET_MINERU_API_TOKEN": "sample-mineru"}),
                  patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sample-deepseek", "KET_CHAT_MODEL": "qwen",
                                          "UNRELATED_VALUE": "sample"}, clear=True)):
                settings.copy_existing()
                self.assertEqual(private.read_text().splitlines(), [
                    "DEEPSEEK_API_KEY=sample-deepseek", "KET_MINERU_API_TOKEN=sample-mineru"])
                with self.assertRaises(settings.ConfigError):
                    settings.copy_existing()

    def test_process_settings_override_private_file_and_windows_user(self):
        with TemporaryDirectory() as temp:
            private = Path(temp) / ".env.local"
            private.write_text('DEEPSEEK_API_KEY=local\nKET_MINERU_API_TOKEN="mineru"\nOTHER=value\n')
            with (patch.object(settings, "PRIVATE_ENV", private),
                  patch.object(settings, "_user_environment", return_value={"KET_CHAT_MODEL": "deepseek-sample"}),
                  patch.dict(os.environ, {"DEEPSEEK_API_KEY": "process"}, clear=True)):
                settings.load_service_env()
                self.assertEqual(dict(os.environ), {"DEEPSEEK_API_KEY": "process", "KET_MINERU_API_TOKEN": "mineru",
                                                    "KET_CHAT_MODEL": "deepseek-sample"})
