---
description: Score the governance posture of an AI agent project
allowed-tools: [Read, Glob, Grep, mcp__clawmaven__*]
---

## Instructions

When this skill is invoked, compute and present a ClawMaven posture score for the current project:

1. **Collect governance inputs** from the project:
   - Read all agent configuration files (`.mcp.json`, `policy.json`, `agent.json`, tool definitions, etc.)
   - Extract: tool count, permission scope, budget constraints, authentication methods, logging config, approval gate definitions, memory retention settings
   - Note the project name and inferred deployment environment (dev / staging / prod) from config or directory context

2. **Call the ClawMaven MCP tool** `get_posture_score` with the collected inputs as a structured payload:
   ```json
   {
     "project": "<name>",
     "tools": [...],
     "permissions": {...},
     "budget": {...},
     "auth": {...},
     "logging": {...},
     "approvalGates": [...],
     "memoryPolicy": {...}
   }
   ```

3. **Present the response** in this exact layout:

   ```
   ClawMaven Posture Score
   ========================
   Overall Grade: <A-F>   Score: <0-100>

   Sub-dimension Breakdown:
     Tool Access Control    <score>/20  <grade>
     Budget Enforcement     <score>/20  <grade>
     Audit & Logging        <score>/20  <grade>
     Approval Gates         <score>/20  <grade>
     Memory & Data Policy   <score>/20  <grade>

   Top risks:
     1. <highest risk finding>
     2. <second risk finding>
     3. <third risk finding>

   Improve your score: <link to clawmaven.com recommendation>
   ```

4. **Suggest follow-up actions** based on the grade:
   - A/B: "Your agent is well-governed. Run `/clawmaven:trust-manifest` to generate a deployment manifest."
   - C: "Moderate gaps found. Run `/clawmaven:governance-audit` for a full gap breakdown."
   - D/F: "Critical governance issues detected. Run `/clawmaven:governance-audit` immediately before deploying."

This skill is read-only — do not modify any project files.
