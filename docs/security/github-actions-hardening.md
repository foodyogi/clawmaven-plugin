# GitHub Actions & Supply-Chain Hardening

This document describes the CI/CD security posture for `clawmaven-plugin` and the conventions any future workflow or package install in this repo must follow.

The plugin itself is just markdown skills and JSON manifests — there is no build, no test runner, and no package manager. Most of what follows is therefore prescriptive ("when you add X, do Y") rather than describing existing pipeline steps.

---

## 1. zizmor — static analysis for workflows

[`zizmor`](https://github.com/zizmorcore/zizmor) is a security linter for GitHub Actions. It catches the common foot-guns: `pull_request_target` with checkout of PR code, `${{ }}` expressions interpolated into shell scripts (template injection), workflows that hand out `write-all` permissions, credentials persisted into `.git/config`, and so on.

It is wired into `.github/workflows/zizmor.yml` and runs on:

- every `pull_request` (including from forks — see §5)
- every `push` to `main`

Findings are uploaded as SARIF to the **Security → Code scanning** tab on GitHub. To see findings:

1. Open the repo on github.com.
2. Go to **Security → Code scanning**. (Public repos get this for free; private repos need GitHub Advanced Security or you can drop `security-events: write` and read the findings from the run log instead.)

### Running zizmor locally

```bash
pipx install zizmor
zizmor .github/workflows/
```

The local CLI uses the same rules as the action, so a clean local run will match CI.

---

## 2. Package minimum release age

When this repo grows a JavaScript dependency surface (it doesn't have one today), use pnpm and configure a **minimum release age** of 4320 minutes (3 days). This is the single most effective mitigation against the "ten-minutes-after-publish" supply-chain attack pattern, where a compromised maintainer publishes a malicious version that gets pulled into CI before anyone notices.

Commit this to the repo so CI, local dev, and agent-driven workflows (Claude Code, Cursor, Replit, Lovable) all honor it. The setting is **pnpm-specific** (pnpm ≥ 10) — yarn and bun do not honor it, and npm's support is recent and version-dependent. If you switch off pnpm later, the setting silently stops protecting you.

`.npmrc`:

```ini
minimum-release-age=4320
```

Or in `package.json`:

```json
{
  "pnpm": {
    "minimumReleaseAge": 4320
  }
}
```

Notes:

- 4320 minutes = 72 hours. If a specific trusted package needs to bypass the delay, use pnpm's `minimumReleaseAgeExclude` for that package rather than lowering the global default.
- The setting is honored at install time. CI must use the same package manager that wrote the config.

---

## 3. Socket Firewall (sfw)

[Socket Firewall Free](https://socket.dev/docs/socket-firewall) is a transparent proxy around package registries. When CI runs `sfw pnpm install`, the firewall blocks installs of packages with known malware, typosquats, or active supply-chain advisories before they ever touch the runner.

When this repo adds JS dependencies, add it to the install step like this (pnpm shown — same shape for `npm ci`, `yarn install --frozen-lockfile`, `bun install --frozen-lockfile`):

```yaml
      - name: Install Socket Firewall
        uses: SocketDev/action@v1
        with:
          mode: firewall

      - name: Install dependencies
        run: sfw pnpm install --frozen-lockfile
```

If a future install step is incompatible with `sfw` (some bundlers and custom registries can be), document the incompatibility in the workflow comment rather than silently dropping the wrapper.

---

## 4. Lockfile discipline

Whatever package manager you reach for, commit the lockfile and install in frozen mode in CI:

| Manager | CI command |
|---|---|
| pnpm | `pnpm install --frozen-lockfile` |
| npm | `npm ci` |
| yarn (classic) | `yarn install --frozen-lockfile` |
| yarn (berry) | `yarn install --immutable` |
| bun | `bun install --frozen-lockfile` |

Never run a bare `pnpm install` / `npm install` in CI — it will silently regenerate the lockfile against whatever the registry currently serves, which defeats both minimum release age and Socket Firewall.

---

## 5. Secret safety in CI

The zizmor workflow uses `on: pull_request`, **not** `pull_request_target`. The difference matters:

- `pull_request` runs in the fork's context: the workflow file from the PR is executed, but `secrets.*` is empty and `GITHUB_TOKEN` is read-only. Safe to run untrusted PR code.
- `pull_request_target` runs in the base repo's context with full secrets and a writable token. If you also `actions/checkout` the PR's code in such a workflow, a fork PR can exfiltrate every secret you own. Do not use this trigger unless you have a very specific reason and you do not check out PR code in the same job.

Other secret-handling rules for this repo:

- Default every workflow to `permissions: contents: read` at the top of the file. Opt in per-job when you genuinely need more.
- Never echo `${{ secrets.* }}` into a shell — GitHub's masking is best-effort and breaks for multi-line or partially-quoted values.
- The plugin's runtime secret, `CLAWMAVEN_TOKEN`, is a *user* environment variable that runs inside the editor. It does **not** belong in this repo's GitHub Actions secrets and no workflow here should reference it.

---

## 6. Action pinning

GitHub Actions resolve by ref at run time. A tag like `@v4` is mutable — the owner can re-point it at a new commit, which is fine for trusted publishers but a known attack vector when an account is compromised (`tj-actions/changed-files` in 2025 is the textbook case).

**This repo pins every third-party action to a full commit SHA**, with the human-readable version in a trailing comment so Dependabot can bump it. zizmor's `unpinned-uses` rule enforces this on every PR; an unpinned `uses:` line will fail CI.

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
- uses: zizmorcore/zizmor-action@5f14fd08f7cf1cb1609c1e344975f152c7ee938d  # v0.5.6
```

Notes:

- The trailing `# vX.Y.Z` comment is **not cosmetic** — Dependabot reads it to compute the next bump. Don't drop it. Don't put anything else on that line.
- `actions/*` (first-party) are lower-risk than third-party actions but get the same treatment. The 2025 incidents all involved the same threat model.
- To resolve a tag to its SHA from the GitHub UI: open the action's `Releases` page, click the tag, the SHA is shown next to the commit hash (or use `git ls-remote https://github.com/OWNER/REPO refs/tags/vX.Y.Z`).

---

## 7. Workflow permissions checklist

Every new workflow added to `.github/workflows/` must:

1. Set `permissions:` at the top of the file (defaulting to `contents: read`).
2. Override per-job only when a step genuinely needs more.
3. Never use `permissions: write-all` or omit the block entirely (which inherits the org/repo default, often `write-all`).

Common per-job opt-ins and when they are justified:

| Permission | When to grant |
|---|---|
| `contents: write` | Cutting a release, committing generated files. Not for CI checks. |
| `pull-requests: write` | Posting a PR comment / labelling. Not for CI checks. |
| `packages: write` | Publishing to GHCR or GitHub Packages. |
| `id-token: write` | OIDC federation to AWS/GCP/PyPI trusted publishing. Never with `pull_request_target`. |
| `security-events: write` | Uploading SARIF to code scanning (this is why the zizmor job grants it). |

---

## 8. Manual GitHub repo settings to enable

These cannot be expressed in the repo and have to be toggled in the GitHub UI:

1. **Settings → Actions → General → Workflow permissions**: set to **Read repository contents and packages permissions** (i.e., default `GITHUB_TOKEN` is read-only). Per-workflow `permissions:` blocks can opt in to more.
2. **Settings → Actions → General → Fork pull request workflows**: set to **Require approval for all outside collaborators** (or stricter). Stops drive-by PRs from running CI without a maintainer's nod.
3. **Settings → Code security → Dependabot**: enable **Dependabot version updates** and add `github-actions` to `.github/dependabot.yml` so tag refs get bumped automatically.
4. **Settings → Code security → Code scanning**: confirm zizmor's SARIF is landing here after the first run on `main`.
5. **Settings → Code security → Secret scanning**: enable, including push protection.
6. **Settings → Branches**: protect `main` with required status checks (include the `zizmor` check once it has run at least once on `main`).

---

## 9. Troubleshooting failed installs

Symptoms and where to look first:

- **`ERR_PNPM_OUTDATED_LOCKFILE`** — the lockfile and `package.json` disagree. Run `pnpm install` locally, commit the updated lockfile, push. Do not "fix" this in CI by dropping `--frozen-lockfile`.
- **`sfw` blocks a package you trust** — Socket logs the rule that fired in the install output. If the block is a false positive, file with Socket *and* temporarily document the bypass in the workflow file (commented `# sfw bypass: socket issue #NNN`) rather than removing `sfw` wholesale.
- **`minimum-release-age` rejects a package** — pnpm refuses to install a version that was published inside the configured window. Either wait, or add a `minimumReleaseAgeExclude` entry for that specific package with a code-review note explaining why the bypass is safe.
- **`actions/checkout` 401** — almost always `permissions: contents: read` was forgotten and the default token has no repo access. Add it.
- **zizmor flags a new finding** — read the rule doc (`zizmor --help` and https://docs.zizmor.sh/audits/), fix the underlying issue. Suppressing with `# zizmor: ignore[rule-id]` is allowed but should carry a one-line comment explaining why.
- **SARIF upload fails with "Resource not accessible by integration"** — the job is missing `security-events: write`, or you're on a private repo without GitHub Advanced Security.

---

## Change log

- 2026-05-20 — Initial hardening pass: added zizmor workflow, documented pnpm `minimum-release-age`, Socket Firewall, lockfile and permissions conventions.
