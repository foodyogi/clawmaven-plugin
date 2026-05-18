# ClawMaven Plugin — Developer Guide

## What this repo is

A Claude Code plugin that surfaces ClawMaven's pre-deployment AI agent governance tooling inside the editor. It is **not** a runtime enforcement layer — it audits, scores, and generates trust manifests for agents your team is building, before those agents ship.

## Repo structure

```
.claude-plugin/plugin.json   — plugin manifest (name, version, author, homepage)
.mcp.json                    — MCP server definition (clawmaven server, 4 tools)
skills/
  governance-audit/SKILL.md  — /clawmaven:governance-audit slash command
  posture-score/SKILL.md     — /clawmaven:posture-score slash command
  trust-manifest/SKILL.md    — /clawmaven:trust-manifest slash command
  config/SKILL.md            — contextual (no slash command), model-invoked
```

## Skills

Skills are markdown files that Claude Code executes as instructions. Each `SKILL.md` has YAML frontmatter with `description` and `allowed-tools`, followed by an `## Instructions` section.

- Three skills have slash commands (`governance-audit`, `posture-score`, `trust-manifest`) — these are user-invoked.
- The `config` skill is contextual — model-invoked when the user edits agent config files. It never announces itself and never calls MCP tools without user intent.

## MCP server

The plugin connects to `https://clawmaven.com/mcp` via HTTP/SSE with Bearer auth (`CLAWMAVEN_TOKEN`). Four tools are exposed:

- `get_posture_score`
- `apply_agent_governance`
- `enforce_budget_cap`
- `generate_trust_manifest`

Skills reference these as `mcp__clawmaven__*` in `allowed-tools`.

## Key constraints

- All audit skills are **read-only** — they never modify project files.
- The `config` skill must not call MCP tools automatically; it surfaces findings inline without blocking the user's primary task.
- `trust-manifest` writes `trust-manifest.json` but must confirm the save location with the user first.
- If `CLAWMAVEN_TOKEN` is unset, surface a clear error with the token URL rather than failing silently.

## Positioning

ClawMaven is upstream of runtime session governance (e.g., protect-mcp). When editing docs or copy, maintain this distinction: ClawMaven is pre-deployment governance design, not runtime enforcement.
