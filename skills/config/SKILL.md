---
description: Automatically detect governance gaps when working on AI agent code
allowed-tools: [Read, Glob, Grep, mcp__clawmaven__*]
---

## Instructions

This skill is model-invoked and runs contextually without a slash command. Do not announce that you are running this skill — surface findings naturally as part of the ongoing conversation.

**Trigger conditions** — activate when Claude observes the developer is actively working on any of:
- `policy.json`, `agent.json`, `agent-config.*`
- `.mcp.json` or any MCP server configuration
- Tool definition files (`tools.json`, `tools/`, `functions.json`)
- Files containing `mcpServers`, `tools`, `permissions`, `budget`, or `approvalGates` keys
- Workflow or orchestration files that define agent behavior

**What to check** (silently, as part of normal code assistance):
- Are budget caps defined? Flag if `budget` key is absent or set to unlimited/null.
- Are approval gates present for destructive tools (write, delete, execute, deploy, send)?
- Is authentication configured for every MCP server connection?
- Is audit logging referenced anywhere in the config?
- Are tool permissions scoped to least privilege, or are wildcard/all-tools permissions used?
- Is a memory or data retention policy declared?

**How to surface findings** — integrate naturally, not as interruptions:
- When editing a config file and you spot a gap, mention it in the same response: "Note: this MCP connection has no authentication — consider adding a bearer token via `CLAWMAVEN_TOKEN`."
- When reviewing agent code and a gap is obvious, add a single-line callout after your main answer.
- Never block the developer's primary task. One concise observation per gap, at most one or two per response.
- If multiple gaps exist, surface the highest-severity one and note "Run `/clawmaven:governance-audit` for a full gap report."

**Do not**:
- Modify config files without being asked
- Call MCP tools automatically without user intent (respect token costs)
- Repeat the same gap warning more than once per session unless the file changes
- Interrupt code-unrelated conversations with governance observations
