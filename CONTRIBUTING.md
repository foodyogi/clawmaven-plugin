# Contributing to the ClawMaven Plugin

Contributor notes only. Claude Code does not load this file into a user's session (a `CLAUDE.md` at the plugin root isn't loaded either, and `claude plugin validate` warns about one), so anything a user's Claude session needs belongs in the relevant `skills/*/SKILL.md`.

## What this repo is

A Claude Code plugin that surfaces ClawMaven's pre-deployment AI agent governance tooling inside the editor. It is **not** a runtime enforcement layer — it audits, scores, and generates trust manifests for agents your team is building, before those agents ship.

## Repo structure

```
.claude-plugin/plugin.json   — Claude Code plugin manifest (name, version, author, homepage)
.mcp.json                    — MCP server definition for Claude Code (clawmaven server, 4 tools)
.cursor-plugin/plugin.json   — Cursor marketplace manifest
mcp.json                     — MCP server definition for Cursor (same content as .mcp.json)
skills/
  governance-audit/SKILL.md  — /clawmaven:governance-audit slash command
  posture-score/SKILL.md     — /clawmaven:posture-score slash command
  trust-manifest/SKILL.md    — /clawmaven:trust-manifest slash command
  config/SKILL.md            — contextual (no slash command), model-invoked
docs/security/               — GitHub Actions / supply-chain hardening conventions
.github/workflows/zizmor.yml — CI: zizmor static analysis of workflows
```

The Claude and Cursor manifests are parallel surfaces: a version bump or description change in `.claude-plugin/plugin.json` must be mirrored in `.cursor-plugin/plugin.json`, and `.mcp.json` / `mcp.json` must stay identical.

## Commands

There is no build, test runner, or package manager — the plugin is markdown skills plus JSON manifests. Useful checks:

- Validate a manifest after editing: `python3 -m json.tool < .mcp.json`
- Lint workflows locally (same rules as CI): `pipx install zizmor && zizmor .github/workflows/`

## Skills

Skills are markdown files that Claude Code executes as instructions. Each `SKILL.md` has YAML frontmatter with `description` and `allowed-tools`, followed by an `## Instructions` section.

- Three skills have slash commands (`governance-audit`, `posture-score`, `trust-manifest`) — these are user-invoked.
- The `config` skill is contextual — model-invoked when the user edits agent config files. It never announces itself and never calls MCP tools without user intent.

## MCP server

The plugin connects to `https://clawmaven.com/mcp` via HTTP/SSE with OAuth: the client prompts the user to connect their ClawMaven account. There is no token environment variable and `.mcp.json` / `mcp.json` must not set an `Authorization` header (a configured header stops Claude Code from using OAuth). Four tools are exposed:

- `get_posture_score`
- `apply_agent_governance`
- `enforce_budget_cap`
- `generate_trust_manifest`

Plugin-provided MCP tools are named `mcp__plugin_<plugin>_<server>__<tool>`, so skills reference these as `mcp__plugin_clawmaven_clawmaven__*` in `allowed-tools` (plugin `clawmaven`, server `clawmaven`).

## Key constraints

- All audit skills are **read-only** — they never modify project files.
- The `config` skill must not call MCP tools automatically; it surfaces findings inline without blocking the user's primary task.
- `trust-manifest` writes `trust-manifest.json` but must confirm the save location with the user first.
- If the ClawMaven server is not connected, tell the user to connect their ClawMaven account when prompted (in Claude Code: run `/mcp` and sign in), and point to https://clawmaven.com/pricing for plans, rather than failing silently.

## CI / workflow conventions

Full details in `docs/security/github-actions-hardening.md`. The rules that apply to every workflow change:

- Pin every action to a full commit SHA with a trailing `# vX.Y.Z` comment (Dependabot reads it — don't drop it). zizmor fails CI on unpinned `uses:`.
- Set `permissions: contents: read` at the top of every workflow; opt in per-job only when needed.
- Use `on: pull_request`, never `pull_request_target`.
- No ClawMaven credential belongs in GitHub Actions secrets or any workflow; users sign in through OAuth in their editor.

## Positioning

ClawMaven is upstream of runtime session governance (e.g., protect-mcp). When editing docs or copy, maintain this distinction: ClawMaven is pre-deployment governance design, not runtime enforcement.
