# ClawMaven Plugin for Claude Code

ClawMaven is a pre-deployment AI agent governance platform that helps teams ship AI agents safely. It audits your agent configurations for governance gaps — missing approval gates, uncapped budgets, unauthenticated tool connections, absent audit logging — scores your overall governance posture on an A–F scale, and generates signed trust manifests that travel with your deployment artifact. ClawMaven connects directly to your Claude Code environment via MCP, so governance checks happen where you build, not after you ship.

ClawMaven governs the AI agents you build, not the coding tool you build them with. Existing governance plugins like protect-mcp secure your Claude Code session — signing tool calls and enforcing Cedar policies within your editor. ClawMaven operates upstream: it audits, scores, and validates the governance posture of the agents your team ships to production. Pre-deployment governance design, not runtime enforcement.

## Installation

```
/plugin install clawmaven@claude-plugins-official
```

After installing, set your ClawMaven API token in your environment:

```bash
export CLAWMAVEN_TOKEN=your_token_here
```

Get a token at [clawmaven.com/tokens](https://clawmaven.com/tokens).

## Available Skills

| Skill | Invocation | Description |
|---|---|---|
| Governance Audit | `/clawmaven:governance-audit` | Audit an AI agent's configuration against ClawMaven standards. Identifies missing approval gates, budget caps, memory policies, and audit logging. |
| Posture Score | `/clawmaven:posture-score` | Score the governance posture of your agent project. Returns an A–F grade with sub-dimension breakdown across tool access, budget enforcement, logging, approval gates, and memory policy. |
| Trust Manifest | `/clawmaven:trust-manifest` | Generate a signed trust manifest for your agent deployment. Captures agent identity, tool access, data access, and risk profile into a portable `trust-manifest.json`. |
| Config Governance | *(contextual — no slash command)* | Automatically surfaces governance gaps as you edit agent configs, MCP server definitions, and tool files. Non-intrusive: one observation per gap, inline with your work. |

## MCP Server

This plugin connects Claude Code to the ClawMaven MCP server:

| Property | Value |
|---|---|
| Server name | `clawmaven` |
| Transport | `url` (HTTP/SSE) |
| Endpoint | `https://clawmaven.com/mcp` |
| Authentication | Bearer token via `CLAWMAVEN_TOKEN` |

**Exposed tools:**

- `get_posture_score` — compute an A–F governance posture score
- `apply_agent_governance` — apply governance policy and return gap analysis
- `enforce_budget_cap` — validate and enforce token/cost budget constraints
- `generate_trust_manifest` — produce a signed, portable trust manifest

The MCP connection is defined in `.mcp.json` at the project root and is loaded automatically by Claude Code when the plugin is active.

## Requirements

- Claude Code (CLI, desktop app, or IDE extension)
- A ClawMaven account and API token ([clawmaven.com](https://clawmaven.com))
- `CLAWMAVEN_TOKEN` set in your shell environment

## Learn More

Visit [clawmaven.com](https://clawmaven.com) for documentation, pricing, and the ClawMaven trust manifest registry.

## License

MIT — Copyright (c) 2026 Master 22 Solutions
