import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

from package_openai import FILES, MCP_URL, REPO, audit, build, default_output


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


    def test_replace_rebuilds_and_failed_rebuild_keeps_previous_zip(self):
        build(self.source, self.output)
        build(self.source, self.output, replace=True)
        before = self.output.read_bytes()
        skill = self.source / "skills" / "posture-score" / "SKILL.md"
        skill.write_text(skill.read_text() + "\nAuthorization: Bearer abcdefghijklmnop\n")
        with self.assertRaises(ValueError):
            build(self.source, self.output, replace=True)
        self.assertEqual(self.output.read_bytes(), before)
        self.assertEqual(list(self.root.glob("*.partial")), [])

    def test_non_square_logo_is_rejected(self):
        logo = self.source / "assets" / "logo.png"
        data = bytearray(logo.read_bytes())
        data[20:24] = (128).to_bytes(4, "big")
        logo.write_bytes(bytes(data))
        with self.assertRaises(ValueError):
            build(self.source, self.output)


class SubmissionAuditTests(unittest.TestCase):
    """The submitted ZIP must contain no lifecycle hooks, app references, or secrets."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        shutil.copytree(REPO / "openai", self.source)

    def assert_clean(self, path):
        audit(path)
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            self.assertFalse([n for n in names if "hook" in n.lower() or n.endswith(".app.json") or n.startswith("apps/")])
            servers = json.loads(archive.read("mcp.json"))["mcpServers"]
            self.assertEqual(servers["clawmaven"]["url"], MCP_URL)

    def test_repository_package_is_clean(self):
        _, output = build(REPO / "openai", self.root / "repo.zip")
        self.assert_clean(output)

    def test_submission_zip_in_dist_is_clean(self):
        manifest = json.loads((REPO / "openai" / "plugin.json").read_text())
        path = default_output(manifest)
        if not path.exists():
            self.skipTest(f"{path} not built; run scripts/build_openai_zip.sh")
        self.assert_clean(path)

    def test_injected_content_is_rejected(self):
        skill = "skills/posture-score/SKILL.md"
        cases = {
            "manifest hook": ("plugin.json", None),
            "frontmatter hook": (skill, "---\nname: posture-score\nhooks:\n  PreToolUse: []\n---\n"),
            "app reference": (skill, "See ./apps/clawmaven.app.json for the app.\n"),
            "bearer token": (skill, "Authorization: Bearer cm_openai_0123456789abcdef\n"),
            "clawmaven token": (skill, "Use cm_tier_0123456789abcdefABCDEF.\n"),
            "openai key": (skill, "sk-proj-0123456789abcdefghij\n"),
            "github token": (skill, "ghp_0123456789abcdefghijklmnopqrstuv\n"),
            "assigned secret": (skill, "CLAWMAVEN_TOKEN=abc123def456ghi789\n"),
            "private key": (skill, "-----BEGIN RSA PRIVATE KEY-----\n"),
        }
        for label, (name, text) in cases.items():
            with self.subTest(label):
                shutil.rmtree(self.source)
                shutil.copytree(REPO / "openai", self.source)
                path = self.source / name
                if text is None:
                    manifest = json.loads(path.read_text())
                    manifest["hooks"] = "./hooks/hooks.json"
                    path.write_text(json.dumps(manifest))
                else:
                    path.write_text(text + path.read_text())
                output = self.root / f"{label.replace(' ', '-')}.zip"
                with self.assertRaises(ValueError):
                    build(self.source, output)
                self.assertFalse(output.exists())

    def test_forbidden_entries_are_rejected(self):
        _, clean = build(REPO / "openai", self.root / "clean.zip")
        for extra in ("hooks/hooks.json", "apps/clawmaven.app.json", ".env"):
            with self.subTest(extra):
                tampered = self.root / "tampered.zip"
                shutil.copy(clean, tampered)
                with zipfile.ZipFile(tampered, "a") as archive:
                    archive.writestr(extra, "{}")
                with self.assertRaises(ValueError):
                    audit(tampered)


if __name__ == "__main__":
    unittest.main()
