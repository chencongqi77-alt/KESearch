from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from deal_survey import settings
from deal_survey.server import make_server


PROJECT = Path(__file__).resolve().parents[1]


class SourceLayoutTests(unittest.TestCase):
    def test_source_commands_work_outside_project_directory(self):
        with TemporaryDirectory() as outside:
            for script, option in (("server.py", "--data-dir"), ("prepare.py", "--mineru-zip"),
                                   ("settings.py", "--copy-existing")):
                with self.subTest(script=script):
                    result = subprocess.run(
                        [sys.executable, "-E", "-B", "-X", "utf8", str(PROJECT / script), "--help"],
                        cwd=outside, capture_output=True, encoding="utf-8", timeout=15,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn(option, result.stdout)
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_static_assets_and_private_config_resolve_after_source_move(self):
        self.assertEqual(settings.PRIVATE_ENV, PROJECT / ".env.local")
        with TemporaryDirectory() as workspace, make_server(Path(workspace), 0) as server:
            for filename in ("index.html", "app.js", "dom.js", "reader-view.js", "style.css"):
                with self.subTest(filename=filename):
                    self.assertTrue((server.web_root / filename).is_file())
