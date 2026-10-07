"""Build the OpenAI draft ZIP from an explicit file list, excluding credentials."""

import argparse
import json
from pathlib import Path
import re
import zipfile

REPO = Path(__file__).resolve().parents[1]
SKILLS = ("governance-audit", "posture-score", "trust-manifest", "budget-check")
FILES = ("plugin.json", "mcp.json") + tuple(f"skills/{name}/SKILL.md" for name in SKILLS)


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
    if not interface.get("displayName") or not interface.get("shortDescription"):
        raise ValueError("Missing OpenAI listing metadata")
    mcp = json.loads((source / "mcp.json").read_text())
    expected = {"clawmaven": {"type": "streamable-http", "url": "https://clawmaven.com/mcp"}}
    if mcp.get("mcpServers") != expected:
        raise ValueError("Expected only ClawMaven HTTPS server without credentials")
    if mcp.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        raise ValueError("Expected portable MCP schema")
    return manifest


def build(source, output):
    manifest = validate(source)
    output = Path(output).resolve()
    if output.is_relative_to(Path(source).resolve()):
        raise ValueError("Write ZIP outside the source package")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation preserves previously generated deliverables.
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(Path(source) / name, name)
        archive.write(REPO / "LICENSE", "LICENSE")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build(REPO / "openai", args.output)
    print(f"Built {args.output}: {manifest['name']} {manifest['version']} (4 skills)")
    print("Draft only; authenticated ChatGPT testing and public review remain pending.")


if __name__ == "__main__":
    main()
