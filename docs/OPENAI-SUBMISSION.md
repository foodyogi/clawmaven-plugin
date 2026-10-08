# OpenAI plugin submission: ClawMaven 0.1.6

Paste-ready fields for the OpenAI plugin dashboard
([Upload and submit](https://developers.openai.com/plugins/deploy/submission)).
Values match `openai/plugin.json`. Character counts and URL checks were run on
2026-10-08.

## Package

| Item | Value |
| --- | --- |
| ZIP | `dist/clawmaven-openai-0.1.6.zip` |
| Rebuild | `scripts/build_openai_zip.sh` (runs the tests, rebuilds the ZIP and icon, audits the ZIP) |
| MCP server | `https://clawmaven.com/mcp` (Streamable HTTP, OAuth), declared in `mcp.json` |
| OAuth client | None in the package. ChatGPT registers through a Client ID Metadata Document (`client_id_metadata_document_supported`, ClawMaven 1.10.30+): public client, PKCE S256, token auth `none`, no client secret |
| Contents | `plugin.json`, `mcp.json`, `assets/logo.png`, four `skills/*/SKILL.md`, `LICENSE` |
| Excluded by audit | lifecycle hooks, `apps/` and `.app.json` references, credentials and secret-like strings |

## Listing fields

**Display name** (9/30)

```
ClawMaven
```

**Subtitle / short description** (30/30)

```
Pre-deploy AI agent governance
```

**Long description** (545/4000)

```
Work with your saved ClawMaven governance profiles before you deploy an AI agent. Get a profile's posture score, grade, and category breakdown; retrieve the effective policy (allowed tools, blocked domains, budget caps, and autonomy level) for an agent you name; check an agent's USD spend against the profile's budget cap; and generate a signed trust manifest for deployment. Recording monthly spend requires your authorization. ClawMaven is pre-deployment governance design: it does not scan code, monitor agents, or enforce policy at runtime.
```

**Developer name** (23/80)

```
Master 22 Solutions LLC
```

**Category**

```
Developer Tools
```

**Capabilities** (Codex only; 5 labels, each at most 120 characters)

```
Posture scores
Effective policy lookup
Per-run budget checks
Monthly spend recording
Signed trust manifests
```

**Default prompts** (3, each at most 128 characters)

```
Get the posture score for my saved ClawMaven governance profile.
Show the effective policy my ClawMaven governance profile applies to my agent.
Generate a signed trust manifest for my agent from its saved ClawMaven governance profile.
```

### URLs

All are HTTPS and returned `200` with no redirect on 2026-10-08.

| Field | URL | Status |
| --- | --- | --- |
| Website | `https://clawmaven.com` | 200 |
| Support | `https://clawmaven.com/help` | 200 |
| Privacy policy | `https://clawmaven.com/privacy` | 200 |
| Terms of service | `https://clawmaven.com/terms` | 200 |

### Icon

`dist/clawmaven-openai-icon.png`: the ClawMaven logo (claw on shield), a
square 256x256 PNG (minimum 48x48), 14,968 bytes. It is the same file as
`openai/assets/logo.png`, which the ZIP uses as `logo` and `composerIcon`.

### Demo video URL

```
https://youtu.be/vU4GuZtE1-o
```

Unlisted on YouTube. It can be viewed without signing in (checked 2026-10-08).

### Claim check

Every description, capability, prompt and release note above follows the
ClawMaven claim rules:

- It never says ClawMaven enforces policy, monitors agents or runs them. Those
  words appear only in negations ("does not ... monitor agents, or enforce
  policy at runtime").
- "Signed" is used only for the trust manifest, which
  `generate_trust_manifest` signs with HMAC-SHA256. No other output is called
  signed.
- It makes no compliance, certification or audit-opinion promises.
- "Check spend against the budget cap" describes an advisory comparison. The
  agent's own runtime applies the cap.

## Test cases

Taken from the eight cases verified live in ChatGPT
(`docs/openai-readiness.md`) on the developer's own profile with agent
`clawmaven-sender`. For review, the prompts use `fd1b292e-cff0-4e87-814a-5238dcea5d47`: the
"Reviewer Sample" profile that `npm run reviewer:create` prints (ClawMaven
1.10.32), which has the same $2.00 per-run cap. Replace the placeholder with
that ID before pasting. Case 3 now expects `get_effective_policy` (ClawMaven
1.10.31) and must be re-run before submission. No case records monthly spend.

### Positive (5)

**1. Posture score**

- description: Retrieve the posture score of a saved governance profile.
- prompt: `What is the posture score for profile fd1b292e-cff0-4e87-814a-5238dcea5d47?`
- tools_triggered: `get_posture_score`
- expected_behavior: Calls `get_posture_score` once with the profile ID and reports the returned profile name, overall score (0–100), letter grade (A–F) and per-category scores. States that this assesses the saved configuration and is not a security scan.

**2. Weakest area and first fix**

- description: Identify the lowest-scoring category of a profile and its recommended fix.
- prompt: `What is the weakest area of profile fd1b292e-cff0-4e87-814a-5238dcea5d47, and what should I fix first?`
- tools_triggered: `get_posture_score`
- expected_behavior: Calls `get_posture_score` and names the lowest-scoring returned category with the fix returned for it. It does not invent categories or fixes.

**3. Effective policy for an agent**

- description: Retrieve the effective policy a profile applies to a named agent.
- prompt: `What tools, blocked domains, and budget caps apply to agent clawmaven-sender under profile fd1b292e-cff0-4e87-814a-5238dcea5d47?`
- tools_triggered: `get_effective_policy`
- expected_behavior: Calls the read-only `get_effective_policy` with the profile ID and agent ID and lists the returned allowed tools, blocked domains, budget caps and autonomy level. It does not claim that enforcement was installed.

**4. Trust manifest**

- description: Generate an HMAC-signed trust manifest for a named agent.
- prompt: `Generate a signed trust manifest for agent clawmaven-sender using profile fd1b292e-cff0-4e87-814a-5238dcea5d47.`
- tools_triggered: `generate_trust_manifest`
- expected_behavior: Calls `generate_trust_manifest` and summarizes the returned agent, profile, posture grade, allowed tools, budget cap, issue time, expiry and signature fields. Before saving `trust-manifest.json` it asks where to save. It does not describe the manifest as proof of runtime enforcement or compliance.

**5. Per-run budget check**

- description: Check one run's spend against the profile's per-run budget cap without recording anything.
- prompt: `Agent clawmaven-sender spent $4.20 on this run under profile fd1b292e-cff0-4e87-814a-5238dcea5d47. Is it within the per-run cap?`
- tools_triggered: `check_budget_cap`
- expected_behavior: Calls the read-only `check_budget_cap` (not `record_monthly_spend`) and reports `over_cap` against the $2.00 per-run cap with the returned spend and remaining amounts. Nothing is recorded. It explains that the decision is advisory and that the agent's runtime applies the cap.

### Negative (3)

No ClawMaven tool should be called.

**6. Unrelated request**

- description: General knowledge request unrelated to agent governance.
- prompt: `Summarize the plot of Hamlet in three sentences.`
- expected behavior: Answers directly without calling any ClawMaven tool.

**7. Runtime enforcement request**

- description: Request for runtime blocking, which ClawMaven does not do.
- prompt: `Block my agent right now if it tries to access the internet.`
- expected behavior: Calls no ClawMaven tool. Explains that ClawMaven is pre-deployment governance design and does not block, monitor or enforce policy on a running agent. It may offer to show the profile's blocked domains so the user can configure their own runtime.

**8. Unrelated writing task**

- description: General writing request unrelated to agent governance.
- prompt: `Draft a short cold email introducing my company to a potential customer.`
- expected behavior: Writes the email without calling any ClawMaven tool.

## Release notes (0.1.6)

```
First public release of the ClawMaven plugin. Connects to your saved ClawMaven governance profiles over OAuth to get a profile's posture score and category breakdown, retrieve the effective policy for a named agent, check a run's USD spend against the per-run budget cap with the read-only check_budget_cap, and generate an HMAC-signed trust manifest. Recording monthly spend uses record_monthly_spend only when you explicitly ask and authorize it, with an idempotency key so a retry is not counted twice. ClawMaven is pre-deployment governance design: it does not monitor agents or enforce policy at runtime.
```

## Reviewer sign-in (OAuth)

Enter credentials in the dashboard's reviewer fields, never in the ZIP or
this file.

| Field | Value |
| --- | --- |
| Login URL | `https://clawmaven.com/oauth/openai/authorize` (ChatGPT opens it on Connect) |
| Username / email | None. ClawMaven sign-in uses an access token, not a username and password. |
| Credential | `<REVIEWER_CLAWMAVEN_ACCESS_TOKEN>` |
| Workspace / tenant | None |
| Sample profile ID | `fd1b292e-cff0-4e87-814a-5238dcea5d47`, printed by `npm run reviewer:create` |
| Agent ID | `clawmaven-sender` (any label works) |

Instructions for the reviewer (paste into the dashboard):

```
Connect ClawMaven, paste the access token on the ClawMaven authorize page, click Authorize ChatGPT and Codex to approve. Use profile fd1b292e-cff0-4e87-814a-5238dcea5d47. Do not use license recovery.
```

Steps in detail:

1. In ChatGPT, install the ClawMaven plugin and select **Connect**.
2. ChatGPT opens `https://clawmaven.com/oauth/openai/authorize`. The page reads
   "Connect ChatGPT and Codex to your governance profiles" and requests the
   `mcp:governance` scope.
3. Paste `<REVIEWER_CLAWMAVEN_ACCESS_TOKEN>` into **ClawMaven access token**.
4. Select **Authorize ChatGPT and Codex**. ClawMaven redirects back to ChatGPT
   with an authorization code, which ChatGPT exchanges with PKCE for an access
   token and a refresh token. The ClawMaven access token itself is not sent to
   ChatGPT.
5. Run the test cases above.

Do not use "recover your license" on the authorization page. It sends an email
link, and the reviewer token is supplied directly instead.

**MFA and email codes:** none. The authorization step accepts only the pasted
access token: no MFA, no email or SMS code, no magic link and no private-network
access (`server/grokOAuth.ts` in the ClawMaven repo, `authorizationPage` and
`/authorize/consent`). The only email-based path is license recovery, which the
reviewer does not need.

## Open items

These need you before submission:

1. **Reviewer credentials.** In the ClawMaven Replit shell, run
   `npm run reviewer:create` (ClawMaven 1.10.32 or later). It creates, or
   reuses, a dedicated Team-tier access token labelled `openai-reviewer` and a
   "Reviewer Sample" profile, and prints both once. Enter the token and the
   profile ID in the dashboard's reviewer fields and replace
   `fd1b292e-cff0-4e87-814a-5238dcea5d47` in the test-case prompts. After the review, run
   `npm run reviewer:revoke`; it disables the token and keeps the profile.
2. **Domain verification.** The dashboard issues a challenge token. ClawMaven
   must serve it as plain text (the exact token only, not JSON) at
   `https://clawmaven.com/.well-known/openai-apps-challenge`, which needs a
   ClawMaven release. That path returns 404 today.
