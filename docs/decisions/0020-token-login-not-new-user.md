# 0020 — Study B logs in with a long-lived token, not a second Linux user

- **Status:** decided
- **Date:** 2026-11-27
- **Supersedes:** 0010 (dedicated `tlsubject` user) and item 1 of 0018 (the `tlsubject` login fix)

## Question

0018 fixed the login clash with a second Linux user (`tlsubject`) on Israr's laptop. That meant sudo, file permissions and a second image copy, and Ammad found it confusing. Is there a simpler fix with the same guarantees?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. Second Linux user `tlsubject` (0010, 0018) | Clean home by construction | Sudo, ACLs, a second image copy, a separate checkout; confusing |
| B. `claude setup-token`: a long-lived subscription token, passed into the container; nothing copied from the host home | One command, once. The token doesn't rotate, so it can't clash with the runner session. The subject's home starts empty: no MCP servers, connectors or settings (0010's goal) | Needs a small fork change (`auth: token`); the token is a secret to keep in a file |

## Decision

B. Decided by Claude (Ammad delegates routine technical calls). It meets both goals of 0010 and 0018 (no clash, clean subject) with one human step instead of about 20.

Built in the fork (`Ammad-Ashraf/Collider-Bench@8c81028`): `auth: token` requires `CLAUDE_CODE_OAUTH_TOKEN`, passes only that into the container, sets `ENABLE_CLAUDEAI_MCP_SERVERS=false`, and copies nothing from the host home (`.claude_token_home` starts empty). The token lives in `~/.config/trust-layer/claude-oauth-token` (mode 600) on the runner, read only by `scripts/study_b.py`, never printed or committed (the script scans every run folder for it before committing). Runner task R5 tests it.
