#!/usr/bin/env python3
"""Fail if any allowed-tools / allowedTools list contains anything other than
Read, Grep, Glob or LS. The Claude plugin directory rejects other entries
(MCP tools, Bash, ${...} paths, // or \\ paths, URLs) from unverified orgs.

Checks YAML frontmatter in *.md files and every key in *.json files.
Usage: python3 scripts/check-allowed-tools.py
"""
import json
import pathlib
import re
import sys

ALLOWED = {"Read", "Grep", "Glob", "LS"}
KEYS = {"allowed-tools", "allowedTools"}
SKIP_DIRS = {".git", "node_modules", "dist"}
ROOT = pathlib.Path(__file__).resolve().parent.parent


def split_entries(value):
    """Turn a frontmatter value ("[A, B]", "A, B", "A B") into entries."""
    value = value.strip().strip("[]")
    return [e.strip().strip("'\"") for e in re.split(r"[,\s]+", value) if e.strip()]


def frontmatter_lists(text):
    if not text.startswith("---"):
        return
    end = text.find("\n---", 3)
    if end == -1:
        return
    lines = text[3:end].splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^\s*(allowed-tools|allowedTools)\s*:\s*(.*)$", line)
        if not m:
            continue
        entries = split_entries(m.group(2))
        # Block-style YAML list on following lines
        for nxt in lines[i + 1:]:
            item = re.match(r"^\s*-\s*(.+)$", nxt)
            if not item:
                break
            entries.append(item.group(1).strip().strip("'\""))
        yield m.group(1), entries


def json_lists(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in KEYS:
                yield k, v if isinstance(v, list) else split_entries(str(v))
            yield from json_lists(v)
    elif isinstance(node, list):
        for v in node:
            yield from json_lists(v)


def main():
    failures, checked = [], 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or SKIP_DIRS & set(path.relative_to(ROOT).parts):
            continue
        rel = path.relative_to(ROOT)
        if path.suffix == ".md":
            found = frontmatter_lists(path.read_text(encoding="utf-8"))
        elif path.suffix == ".json":
            try:
                found = json_lists(json.loads(path.read_text(encoding="utf-8")))
            except ValueError as e:
                failures.append(f"{rel}: invalid JSON ({e})")
                continue
        else:
            continue
        for key, entries in found:
            checked += 1
            bad = [e for e in entries if e not in ALLOWED]
            if bad:
                failures.append(f"{rel}: {key} has disallowed entries {bad}")

    for f in failures:
        print(f"FAIL {f}")
    if failures:
        print(f"{len(failures)} problem(s); allowed entries are {sorted(ALLOWED)}")
        return 1
    print(f"OK: {checked} allowed-tools list(s) checked, all within {sorted(ALLOWED)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
