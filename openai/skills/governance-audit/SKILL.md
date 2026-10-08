---
name: governance-audit
description: Read the effective policy a saved ClawMaven governance profile sets for a named agent, using the read-only get_effective_policy.
---

# Governance Audit

Use when the user asks what policy a saved ClawMaven governance profile sets for an agent. This reads the intended policy before deployment; it does not scan code, apply or enforce the policy, or monitor the agent. The agent's runtime applies it.

1. Obtain the exact saved `profileId`. Use `clawmaven://policies` if resource reads are supported to list accessible profiles; ask the user to select when ambiguous. Otherwise ask for the ID. Never invent a profile ID.
2. Obtain an `agentId`. This is a label the user chooses for the agent (for example, its name); it does not need to exist on the server beforehand. Ask if none was given rather than inventing one.
3. Inspect the connected tool schema and call `get_effective_policy` with `{"profileId":"<profile>","agentId":"<agent>"}` and optional `runtime` if the schema accepts it. The tool takes only these identifiers; do not send configuration files or gap lists.
4. Present the returned allowed tools, blocked domains, budget caps, and autonomy level exactly as returned.
5. If the user asks, compare the returned policy with agent configuration they supply. Present that comparison as your own reading of their files, not as a ClawMaven result, and do not modify files or deploy.

If the connection is unavailable or authentication fails, direct the user to the host's ClawMaven connection settings. Never request tokens or passwords in chat. For missing or inaccessible profiles, clarify or report denial without probing other IDs. Report tool errors accurately; never manufacture results.
