# Smoke run notes — 2026-11-18, runner laptop

Plumbing test for milestone M1. Carry the durable points into `experiments/00-smoke-run/README.md`, `lab-log.md` and the roadmap on the Windows laptop (the runner commits only under `runs/`).

## What ran

`scripts/run-agent --config harness-config.yaml`, i.e. Collider-Bench's `configs/claude.yaml` with `model: claude-sonnet-4-6` and `auth: oauth`. Task `sus-16-046_sim-T5Wg` (Ammad's choice, replacing sus-16-034: it is Collider-Bench's own smoke task). No checker.

## Numbers

| | |
| --- | --- |
| Wall-clock | 27.8 min (cap 2.5 h) |
| Turns | 107 (88 Bash, 9 Write, 8 Read) |
| API-equivalent cost | $5.68 (billed to the Max 5x subscription instead) |
| N_gen | 10,000 (agent's choice) |
| Score | 4/4 bins; δ_norm = 0.98; norm rel. L² = 0.995; shape rel. L² = 0.92 → **fail** |
| Disk | 1.4 GB per run |

The Haiku 4.5 Stop-hook test cost a further $0.03.

## Research findings (one run: a hint, not evidence)

1. **The normalization error came from ε, not from σ, L or units.** σ = 3.96 fb (Prospino NLO 0.00396 pb, correct pb→fb), L = 35.9 fb⁻¹, mass point correct, BRs consistent. The yield is ~50× low because only 0.93% of events pass the signal region, against ~38.6% implied by the reference. δ_norm still reads as a big "normalization" failure.
2. **Implication for Phase 1:** checks C1–C5 as designed would pass this run, because every recorded factor is "right" except the efficiency, which the pipeline computes. If baseline failures are mostly ε/kinematics rather than 1a–1e, Study B has a power problem (the risk the plan already names). Worth checking in the paper's per-task tables before committing to tasks, and worth a lead discussion: a cheap acceptance sanity check (3c) may catch more than C1–C5 on real runs.
3. Draft label in `labels.yaml`: 3c (proposed). Root cause of the low acceptance not found yet; that is the M3 transcript read.

## Setup problems hit (and fixes)

1. **No container engine and no `python3-venv`** on the runner. Fixed: `sudo apt install podman passt python3.14-venv` (run by Ammad; the Claude sandbox cannot use sudo). Host Python is 3.14, outside Collider-Bench's CI matrix (3.10–3.12), but all 231 offline tests and 24 image tests pass.
2. **Image is larger than documented:** 3.9 GB compressed download (docs: ~3.5 GB), 8.5 GB unpacked; took ~1 h at 1–3 MB/s.
3. **The image has no `claude` baked in** (`/opt/node-global/bin` absent, despite `docker/README.md`). The harness bind-mounts the host binary (`~/.local/share/claude/versions/2.1.326`); it runs fine in the image (Ubuntu 20.04, glibc 2.31).
4. **OAuth leaks host config into the subject agent.** The harness copies the host `~/.claude.json` and `~/.claude/settings.json` into the fake `$HOME`. On this host that meant the Mattermost MCP server (with auth headers) and, by default, the account's claude.ai connectors (Gmail, Drive, Vercel, Supabase…), all with `--dangerously-skip-permissions`. Fixed for this run only: removed Mattermost from user scope and set `ENABLE_CLAUDEAI_MCP_SERVERS=false`; the init event confirmed `mcp_servers: []`. Both restored after the run. **Needs a permanent design before baseline and Study B runs** (see attachment point 2).
5. **OAuth refresh-token race:** the host access token had 1.3 h left at launch. A run longer than that would have both the host and the container refreshing the same rotating token. Did not happen (28 min), but measured runs on OAuth should start right after a fresh login, or use an API key.
6. **The CLI is much newer than in the paper:** Claude Code 2.1.326 gives the subject agent tools such as `RemoteTrigger`, `PushNotification`, `CronCreate`, `SendMessage`, `Workflow` and built-in skills. This is a confounder against the paper's numbers (same for both arms, so it does not bias Study B's comparison), and those tools touch the account. Consider `--disallowedTools` for them in a derived config.
7. Pricing warning in the harness (DeepSeek promo rates stale): irrelevant for Claude runs.

## Decisions this unblocks (for Ammad)

- 0005 Study B model / 0006 budget: one Sonnet 4.6 run at max effort ≈ $5.7 API-equivalent and 28 min on 32 threads. 18 runs ≈ $100 at that rate, before longer runs or a 128-core rental.
- Auth for measured runs: OAuth worked, but points 4–5 above argue for an API key, or a dedicated runner OS user, for Study B.
