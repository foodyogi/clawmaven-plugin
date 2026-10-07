# OpenAI plugin draft: 0.1.0

## Delivery status

Prepared in an isolated copy under this chat's `work/clawmaven-plugin` directory
after automatic approval review rejected direct file edits outside the project.
The original plugin repo was fetched and was clean/up to date, then switched to
`feat/openai-plugin`; its files have no draft edits. Nothing was pushed or deployed.
The delivered patch can apply the draft to that repo after the write restriction
is resolved. The existing app was inspected only.

Verification completed: four packaging tests passed, both portable JSON manifests
validated against their published Agent Plugins schemas, all four skill headers
parsed as YAML with matching names, and the generated archive passed CRC checks.
This does not establish OpenAI approval or authenticated functionality.

The OpenAI package lives in `openai/` in the plugin repository. Its portable
manifest and MCP configuration are separate from the existing Claude and Cursor
packages. The hosted governance engine remains in the ClawMaven application.

## Build

Python 3.9 or later, without third-party dependencies:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/package_openai.py --output /absolute/output/path/clawmaven-openai-0.1.0.zip
```

Only two manifests, four skills, and the license are packaged. Extra files and
credential-bearing MCP settings are excluded or rejected. Existing archives are
not overwritten. These are local structural checks, not complete JSON Schema
validation or OpenAI's submission checks.

The repo marketplace `.agents/plugins/marketplace.json` points to `./openai`.
Open the repo as a trusted project in a supported desktop client to discover it.
Installation does not establish server authentication compatibility.

## Findings

Checked app source at `2c8f27b` and public endpoints on 2026-10-02 UTC
(2026-10-01 in America/Bogota).

| Area | Result | Evidence / next step |
| --- | --- | --- |
| Remote transport | Ready | `/mcp/info` returns 200, version 1.10.19, Streamable HTTP, four tools. |
| Skill inputs | Corrected in this draft | Tools require saved profile IDs. Original Claude skills send unsupported config payloads; those packages were not edited. |
| ChatGPT account linking | Blocker | Unauthenticated initialization returns 401 without `WWW-Authenticate`; `/.well-known/oauth-protected-resource` returns 404. |
| Existing OAuth | Server work needed | `server/grokOAuth.ts` fixes the client to `clawmaven-grok-web` and a Grok redirect URI. It is not a general OpenAI client integration. |
| Tool metadata | Server work needed | `mcp/tools.ts` lacks explicit annotations and OAuth security declarations. Monthly budget checks record spend; all tools also write audit events. |
| Outputs | Review needed | Tools return JSON text; review structured output schemas/content and error handling. |
| Listing | Incomplete | Privacy route exists. Confirm support and terms URLs; add icons and demonstration media; verify publisher identity in the portal. |
| Authenticated tests | Pending | No authorized review account/profile was available. Tool calls and ChatGPT linking have not been tested. |

## Backend work before connection testing

Implement an OpenAI-compatible OAuth 2.1 authorization-code flow with S256 PKCE,
protected-resource and authorization-server discovery, Bearer challenges, and
resource-bound tokens. Choose predefined clients, CIMD, or DCR deliberately.
Preserve Grok clients, tenant isolation, existing tokens, entitlement checks,
refresh, and revocation. Add appropriate tool auth metadata and annotations.
Test redirects, expiry, cross-tenant denials, and budget mutation behavior.

This draft does not implement or deploy backend changes. Do not enable anonymous
access as a workaround. Never embed credentials in the ZIP or ask users to paste
tokens into chat. Configure authentication through the host's connection settings.

## Reviewer scenarios

Proposed cases only, not completed tests. Use a dedicated reviewer account with
synthetic profiles and agents. Run and record results after authentication works.

### Five positive cases

| Prompt / scenario | Expected operation | Expected outcome |
| --- | --- | --- |
| Review this agent configuration for governance gaps. | Local review; no MCP call unless comparison requested. | Evidence-based findings, missing vs unknown controls distinguished, files unchanged. |
| Score profile `<owned-profile-id>`. | `get_posture_score` with `profileId`. | Returned overall, grade, and categories without invented weights. |
| Compare agent `<agent-id>` with profile `<owned-profile-id>`. | `apply_agent_governance` with profile and agent IDs. | Effective policy compared with configuration; no claim enforcement was installed. |
| Check this run's $0.25 spend for agent `<agent-id>` against profile `<owned-profile-id>`. | `enforce_budget_cap` with `scope: per_run`. | Actual decision, cap, remaining USD; no monthly recording. |
| Generate a trust manifest for agent `<agent-id>` using profile `<owned-profile-id>`. | `generate_trust_manifest`. | Real signed response and expiry; file save only after location approval; signing failures reported. |

### Three negative cases

| Prompt / scenario | Expected behavior |
| --- | --- |
| Score my profile, with multiple possible profiles. | Ask the user to choose; no invented IDs or score. |
| Use another customer's profile, or access denied. | Report denial without bypassing authorization or probing other IDs. |
| Check my monthly budget, without authorization to record spend. | Explain that the current tool records an increment; clarify amount and obtain authorization before calling. |

Also test authorized monthly recording and same-key retries to verify spend is
not counted twice. Keep reviewer credentials outside the package. Complete the
portal's five positive and three negative test cases, recording URL, release
notes, domain verification, listing details, and review account setup before
submission.

## Release notes

0.1.0 is an unpublished draft with portable OpenAI metadata, a remote MCP
connection, four skills matched to current server contracts, a repo marketplace,
an allowlisted ZIP builder, and packaging tests. Authentication and directory
review remain pending.

## Official references

- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Authenticate users](https://developers.openai.com/plugins/build/auth)
- [Upload and submit](https://developers.openai.com/plugins/deploy/submission)
