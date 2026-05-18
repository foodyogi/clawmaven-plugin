---
description: Audit an AI agent's governance configuration against ClawMaven standards
allowed-tools: [Read, Glob, Grep, mcp__clawmaven__*]
---

## Instructions

When this skill is invoked, perform a full governance audit of the current project's AI agent configuration:

1. **Discover agent config files** — search the project for agent configuration files including:
   - `policy.json`, `agent.json`, `agent-config.*`
   - `.mcp.json`, `mcp.json`
   - Tool definition files (`tools.json`, `tools/`, `functions.json`)
   - Any file referencing `mcpServers`, `tools`, `permissions`, or `budget`

2. **Identify governance gaps** across these dimensions:
   - **Approval gates** — Are there human-in-the-loop checkpoints for high-risk actions? Flag if absent.
   - **Budget caps** — Are token, cost, or time budgets defined and enforced? Flag if absent or unbounded.
   - **Memory policy** — Is there an explicit data retention and memory scope policy? Flag if absent.
   - **Audit logging** — Are agent actions logged to a durable, tamper-evident store? Flag if absent.
   - **Tool access scope** — Are tool permissions least-privilege? Flag overly broad permissions.
   - **Authentication** — Are all MCP server connections authenticated? Flag unauthenticated connections.

3. **Call the ClawMaven MCP tool** `apply_agent_governance` with the extracted config and gap list.

4. **Present findings** in this format:
   - Overall governance status (PASS / WARN / FAIL)
   - Numbered list of gaps found, each with severity (CRITICAL / HIGH / MEDIUM / LOW)
   - Recommended remediations for each gap
   - A next-step prompt: "Run `/clawmaven:posture-score` to get your A-F grade, or `/clawmaven:trust-manifest` to generate a deployment manifest."

Do not modify any project files during the audit — this skill is read-only. Surface all findings as structured output in the conversation.
