import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from package_openai import FILES, REPO, build


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        shutil.copytree(REPO / "openai", self.source)
        self.output = self.root / "clawmaven.zip"

    def test_only_allowlisted_files_are_shipped(self):
        (self.source / ".env").write_text("PRIVATE_TEST_VALUE=do-not-package")
        (self.source / "unrelated.txt").write_text("do not package")
        build(self.source, self.output)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(set(archive.namelist()), set(FILES) | {"LICENSE"})
            self.assertIsNone(archive.testzip())
        with self.assertRaises(FileExistsError):
            build(self.source, self.output)

    def test_credentials_in_mcp_config_are_rejected(self):
        path = self.source / "mcp.json"
        config = json.loads(path.read_text())
        config["mcpServers"]["clawmaven"]["headers"] = {"Authorization": "Bearer test"}
        path.write_text(json.dumps(config))
        with self.assertRaises(ValueError):
            build(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_missing_skill_is_rejected_before_output(self):
        (self.source / FILES[-1]).unlink()
        with self.assertRaises(ValueError):
            build(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_listing_metadata_meets_submission_limits(self):
        build(self.source, self.output)
        path = self.source / "plugin.json"
        manifest = json.loads(path.read_text())
        manifest["extensions"]["com.openai"]["interface"]["shortDescription"] = "x" * 31
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            build(self.source, self.root / "too-long.zip")

    def test_logo_is_shipped_and_required(self):
        build(self.source, self.output)
        with zipfile.ZipFile(self.output) as archive:
            self.assertIn("assets/logo.png", archive.namelist())
        (self.source / "assets" / "logo.png").unlink()
        with self.assertRaises(ValueError):
            build(self.source, self.root / "no-logo.zip")

    def test_symlink_escape_is_rejected(self):
        directory = self.source / "skills" / "budget-check"
        external = self.root / "external"
        shutil.move(directory, external)
        directory.symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            build(self.source, self.output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
