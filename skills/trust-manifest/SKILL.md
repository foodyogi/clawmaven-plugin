---
description: Generate a signed trust manifest for an AI agent deployment
allowed-tools: [Read, Glob, Grep]
---

## Instructions

When this skill is invoked, generate a ClawMaven trust manifest for the current project:

1. **Gather agent identity and profile** from the project:
   - **Identity**: agent name, version, project path, inferred deployment environment
   - **Tool access**: all MCP servers and tools declared in `.mcp.json` or equivalent config, including transport type and authentication method
   - **Data access**: files, APIs, databases, or external services the agent can reach based on tool definitions and permissions
   - **Risk profile**: tool count, presence of destructive actions (write, delete, execute, deploy), external network access, authentication gaps
   - **Governance controls**: budget caps, approval gates, memory policy, audit logging — present or absent

2. **Call the ClawMaven MCP tool** `mcp__plugin_clawmaven_clawmaven__generate_trust_manifest` with the assembled profile:
   ```json
   {
     "agent": {
       "name": "<name>",
       "version": "<version>",
       "environment": "<dev|staging|prod>"
     },
     "toolAccess": [...],
     "dataAccess": [...],
     "riskProfile": {...},
     "governanceControls": {...}
   }
   ```

3. **Save the returned manifest** to the project as `trust-manifest.json` in the project root (or a `governance/` subdirectory if one exists). Ask the user to confirm the save location before writing.

4. **Present a summary** of the manifest contents:
   - Manifest ID and timestamp
   - Signing status (signed / unsigned — depends on the connected ClawMaven plan)
   - Risk tier (LOW / MEDIUM / HIGH / CRITICAL)
   - List of declared tool and data access scopes
   - Governance controls attested

5. **Advise on next steps**:
   - Commit `trust-manifest.json` to version control so it travels with the deployment artifact
   - Re-generate after any change to tool definitions, permissions, or governance config
   - Link to clawmaven.com for manifest verification and registry lookup

If the ClawMaven MCP server is not connected, surface a clear error: "Connect your ClawMaven account when prompted (in Claude Code, run /mcp and sign in to clawmaven). Connecting needs a paid plan: https://clawmaven.com/pricing"
