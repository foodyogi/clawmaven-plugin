"""Build the OpenAI plugin ZIP from an explicit file list, excluding credentials."""

import argparse
import json
import os
from pathlib import Path
import re
import struct
import zipfile

REPO = Path(__file__).resolve().parents[1]
SKILLS = ("governance-audit", "posture-score", "trust-manifest", "budget-check")
FILES = ("plugin.json", "mcp.json", "assets/logo.png") + tuple(
    f"skills/{name}/SKILL.md" for name in SKILLS
)
# Listing limits from OpenAI's submission docs ("Listing metadata").
TEXT_LIMITS = {"displayName": 30, "shortDescription": 30, "longDescription": 4000, "developerName": 80}
URL_FIELDS = ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL")
MCP_URL = "https://clawmaven.com/mcp"
# Submission rules: no lifecycle hooks, no app references, no credentials in the ZIP.
FORBIDDEN_TEXT = {
    "lifecycle hook": re.compile(r'"hooks"\s*:|^\s*hooks\s*:', re.M),
    "app reference": re.compile(r'\.app\.json|"apps"\s*:'),
    "bearer credential": re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{8,}"),
    "ClawMaven credential": re.compile(r"\bcm_[A-Za-z0-9_]*[A-Za-z0-9]{16,}"),
    "API key": re.compile(r"\b(sk|rk|pk)-[A-Za-z0-9_-]{16,}|\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{20,}|\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "assigned secret": re.compile(
        r"(?i)(api[_-]?key|secret|password|passwd|token|signing[_-]?key)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{8,}"
    ),
}


def validate(source):
    source = Path(source).resolve()
    for name in FILES:
        path = source / name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing or symlinked package file: {name}")
        if not path.resolve().is_relative_to(source):
            raise ValueError(f"Package file escapes source directory: {name}")
    manifest = json.loads((source / "plugin.json").read_text())
    if manifest.get("name") != "clawmaven" or not re.fullmatch(
        r"\d+\.\d+\.\d+", manifest.get("version", "")
    ):
        raise ValueError("Expected clawmaven identity and numeric release version")
    if manifest.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        raise ValueError("Expected portable Agent Plugins schema")
    interface = manifest["extensions"]["com.openai"]["interface"]
    for field, limit in TEXT_LIMITS.items():
        if not 0 < len(interface.get(field, "")) <= limit:
            raise ValueError(f"{field} must be 1-{limit} characters")
    for field in URL_FIELDS:
        if not interface.get(field, "").startswith("https://"):
            raise ValueError(f"{field} must be an HTTPS URL")
    prompts = interface.get("defaultPrompt", [])
    if len(prompts) > 3 or any(len(prompt) > 128 for prompt in prompts):
        raise ValueError("Use at most three default prompts of 128 characters or fewer")
    if interface.get("logo") != "./assets/logo.png":
        raise ValueError("Expected logo at ./assets/logo.png")
    width, height = png_size((source / "assets/logo.png").read_bytes())
    if width != height or not 48 <= width <= 4096:
        raise ValueError("Logo must be a square PNG from 48x48 to 4096x4096 pixels")
    mcp = json.loads((source / "mcp.json").read_text())
    expected = {"clawmaven": {"type": "streamable-http", "url": MCP_URL}}
    if mcp.get("mcpServers") != expected:
        raise ValueError("Expected only ClawMaven HTTPS server without credentials")
    if mcp.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        raise ValueError("Expected portable MCP schema")
    return manifest


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Logo must be a PNG")
    return struct.unpack(">II", data[16:24])


def default_output(manifest):
    return REPO / "dist" / f"clawmaven-openai-{manifest['version']}.zip"


def audit(archive_path):
    """Reject a built ZIP that contains hooks, app references, or secret-like strings."""
    problems = []
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if sorted(names) != sorted(FILES + ("LICENSE",)):
            problems.append(f"unexpected entries: {sorted(set(names) ^ set(FILES + ('LICENSE',)))}")
        for name in names:
            parts = Path(name).parts
            if any(part in ("hooks", "hooks.json", "apps", ".app.json") or part.endswith(".app.json") for part in parts):
                problems.append(f"{name}: forbidden path")
            if any(part.startswith(".env") for part in parts):
                problems.append(f"{name}: environment file")
            if name.endswith(".png"):
                continue
            text = archive.read(name).decode("utf-8")
            for label, pattern in FORBIDDEN_TEXT.items():
                match = pattern.search(text)
                if match:
                    problems.append(f"{name}: {label} ({match.group(0)[:24]}...)")
        if "mcp.json" in names:
            servers = json.loads(archive.read("mcp.json")).get("mcpServers", {})
            if [server.get("url") for server in servers.values()] != [MCP_URL]:
                problems.append(f"mcp.json must declare only {MCP_URL}")
    if problems:
        raise ValueError("ZIP failed submission audit:\n  " + "\n  ".join(problems))


def build(source, output=None, replace=False):
    manifest = validate(source)
    output = Path(output or default_output(manifest)).resolve()
    if output.is_relative_to(Path(source).resolve()):
        raise ValueError("Write ZIP outside the source package")
    if output.exists() and not replace:
        # Preserve previously generated deliverables unless a rebuild is requested.
        raise FileExistsError(f"{output} exists; pass --replace to rebuild it")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.with_name(output.name + ".partial")
    try:
        with zipfile.ZipFile(staging, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in FILES:
                archive.write(Path(source) / name, name)
            archive.write(REPO / "LICENSE", "LICENSE")
        audit(staging)
        os.replace(staging, output)
    finally:
        staging.unlink(missing_ok=True)
    return manifest, output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="default: dist/clawmaven-openai-<version>.zip")
    parser.add_argument("--replace", action="store_true", help="overwrite an existing ZIP")
    args = parser.parse_args()
    manifest, output = build(REPO / "openai", args.output, args.replace)
    print(f"Built {output} ({output.stat().st_size} bytes): {manifest['name']} {manifest['version']} (4 skills)")
    print("Upload this ZIP in the OpenAI portal; see docs/OPENAI-SUBMISSION.md for the listing fields.")


if __name__ == "__main__":
    main()
