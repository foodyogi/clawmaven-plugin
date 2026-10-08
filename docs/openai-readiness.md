# OpenAI plugin: 0.1.3

## Status

Submission candidate. OAuth account linking is verified end to end in ChatGPT,
all eight review test cases pass (case 5 re-verified live Oct 8 2026 with check_budget_cap), and the terms
of service and privacy policy are live. Nothing has been submitted to OpenAI yet.

The OpenAI package lives in `openai/`, separate from the Claude and Cursor
packages. The hosted governance engine remains in the ClawMaven application.

## Layout

Follows the Agent Plugins format in OpenAI's
[Package your plugin](https://developers.openai.com/plugins/build/plugins)
("Plugin structure", "Add OpenAI-specific metadata", "Path rules"): a root
`plugin.json` with OpenAI listing fields under `extensions.com.openai.interface`,
a root `mcp.json`, skills discovered from `skills/`, and images in `assets/`.
`.codex-plugin/plugin.json` is only a compatibility fallback in that format and
is not needed; `extensions.com.openai` replaces it when present.

```
openai/
  plugin.json
  mcp.json
  assets/logo.png          256x256 PNG, used as logo and composerIcon
  skills/<name>/SKILL.md   posture-score, governance-audit, budget-check, trust-manifest
```

Listing fields and limits follow
[Upload and submit](https://developers.openai.com/plugins/deploy/submission)
("Listing metadata", "Icons and screenshots"). The packager enforces the text
limits (`displayName` and `shortDescription` at most 30 characters), HTTPS
website, support, privacy, and terms URLs, at most three default prompts of 128
characters, and the presence of the logo.

## Build

Python 3.9 or later, without third-party dependencies:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/package_openai.py --output /absolute/output/path/clawmaven-openai-0.1.3.zip
```

Only the two manifests, the logo, four skills, and the license are packaged.
Extra files and credential-bearing MCP settings are excluded or rejected.
Existing archives are not overwritten.

The repo marketplace `.agents/plugins/marketplace.json` points to `./openai`.

## Tools

The live server at `https://clawmaven.com/mcp` (Streamable HTTP, OAuth) exposes
the tools below. Every tool needs a saved `profileId`; all but
`get_posture_score` also need an `agentId`, which is a label the caller chooses.

| Tool | Access | Skill | Default prompt |
| --- | --- | --- | --- |
| `get_posture_score` | Read | posture-score | Get the posture score for my saved ClawMaven governance profile. |
| `apply_agent_governance` | Read | governance-audit | Show the effective policy my ClawMaven governance profile applies to my agent. |
| `generate_trust_manifest` | Read | trust-manifest | Generate a signed trust manifest for my agent from its saved ClawMaven governance profile. |
| `check_budget_cap` | Read | budget-check | None. |
| `enforce_budget_cap` | Write (monthly scope) | budget-check | None; recording spend needs authorization. |

`check_budget_cap` (ClawMaven 1.10.28) compares a run's spend with the per-run
cap and records nothing; the skill uses it for every per-run question.
`enforce_budget_cap` is used only when the user explicitly asks to record
monthly spend: `scope: "monthly"` records a spend increment and requires the
user's authorization and an idempotency key. No tool scans code, monitors agents, or
enforces policy at runtime.

## Readiness

| Area | Status |
| --- | --- |
| Remote transport | Ready. `/mcp/info` reports Streamable HTTP and the tools above. |
| OAuth account linking | Verified live in ChatGPT. Unauthenticated requests return 401 with a `WWW-Authenticate` Bearer challenge pointing to `/.well-known/oauth-protected-resource/mcp`. |
| Review test cases | 8 of 8 verified live; case 5 verified live Oct 8 2026 against `check_budget_cap`. |
| Terms and privacy | Live: `https://clawmaven.com/terms`, `https://clawmaven.com/privacy`. |
| Support URL | `https://clawmaven.com/help` (live). |
| Logo | `assets/logo.png`, 256x256 PNG. |
| Screenshots | Optional; none included. |
| Portal steps | Domain verification, publisher identity, and reviewer account setup are done in the OpenAI portal at submission. |

## Review test cases

These eight cases were run and verified live in ChatGPT with profile
`05dea91f-bbbe-4ecc-951b-bdca2a0da476` and agent `clawmaven-sender`. Case 5 now
expects `check_budget_cap` and must be re-run once ClawMaven 1.10.28 is live.
No case records monthly spend.

### Positive

| # | Prompt | Expected tool | Expected outcome |
| --- | --- | --- | --- |
| 1 | What is the posture score for profile `05dea91f-bbbe-4ecc-951b-bdca2a0da476`? | `get_posture_score` | Returned overall score, grade, and categories. |
| 2 | What is the weakest area of profile `05dea91f-bbbe-4ecc-951b-bdca2a0da476`, and what should I fix first? | `get_posture_score` | Lowest-scoring returned category and its returned fix. |
| 3 | What tools, blocked domains, and budget caps apply to agent `clawmaven-sender` under profile `05dea91f-bbbe-4ecc-951b-bdca2a0da476`? | `apply_agent_governance` | Returned allowed tools, blocked domains, and budget caps; no claim that enforcement was installed. |
| 4 | Generate a signed trust manifest for agent `clawmaven-sender` using profile `05dea91f-bbbe-4ecc-951b-bdca2a0da476`. | `generate_trust_manifest` | Signed manifest with issue time and expiry. |
| 5 | Agent `clawmaven-sender` spent $4.20 on this run under profile `05dea91f-bbbe-4ecc-951b-bdca2a0da476`. Is it within the per-run cap? | `check_budget_cap` | `over_cap` against the $2.00 per-run cap; nothing recorded. **Re-run pending.** |

### Negative

No ClawMaven tool should be called.

| # | Prompt | Expected behavior |
| --- | --- | --- |
| 6 | Summarize the plot of Hamlet in three sentences. | Answered without ClawMaven tools. |
| 7 | Block my agent right now if it tries to access the internet. | Explains that ClawMaven does not enforce policy at runtime. |
| 8 | Draft a short cold email introducing my company to a potential customer. | Answered without ClawMaven tools. |

## Release notes

0.1.3 (2026-10-08): The budget-check skill uses the read-only `check_budget_cap`
(ClawMaven 1.10.28) for per-run questions and `enforce_budget_cap` only when the
user explicitly asks to record monthly spend. Case 5 expects `check_budget_cap`;
verified live Oct 8 2026 (check_budget_cap).

0.1.2 (2026-10-07): Readiness test cases replaced with the 8 verified ChatGPT
cases (profile 05dea91f…, agent clawmaven-sender).

0.1.1: Adds terms of service and support URLs, a logo, and enforced listing
limits (short description shortened to 30 characters). Default prompts, the
descriptions, and all four skills now match the four live tools; the
configuration-review prompt is replaced with an effective-policy lookup.

0.1.0: Unpublished draft with portable OpenAI metadata, a remote MCP connection,
four skills, a repo marketplace, an allowlisted ZIP builder, and packaging tests.

## Official references

- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Authenticate users](https://developers.openai.com/plugins/build/auth)
- [Upload and submit](https://developers.openai.com/plugins/deploy/submission)
