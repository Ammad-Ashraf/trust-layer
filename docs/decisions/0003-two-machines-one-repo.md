# 0003 — Two machines, one repo

- **Status:** decided
- **Date:** 2026-11-13

## Decision

| Machine | Job |
| --- | --- |
| Ammad's Windows laptop (Claude Code Local) | All development and Study A. The only place code is edited |
| Friend's Linux laptop (SSH from Claude Desktop; Tailscale if on different networks) | Only runs things: smoke run, baselines, gate tests |
| Rented 128-vCPU instance | Study B's 18 measured runs only |

- One GitHub repo connects them. The runner commits only under `experiments/*/runs/`.
- The test-subject agent uses a separate, spend-limited Anthropic API key, revoked when Phase 1 ends.
- Backup if the runner is unavailable: WSL2 + Docker Desktop on Ammad's laptop.
- Cloud sessions are not used for runs (limited network access; not built for the physics container).
