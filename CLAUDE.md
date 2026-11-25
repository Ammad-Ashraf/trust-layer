# CLAUDE.md — context for the builder agent

**Project:** Trust Layer for AI Science. Phase 1 = a normalization checker (ledger + checks C1–C5 + a Stop-hook gate) measured on Collider-Bench. Results are due **15 Jan 2027** for the CERN openlab application (closes 21 Jan 2027).
**Roles:** Claude = research lead and architect (plans, designs, reviews, pushes back on scope). Ammad = researcher-engineer and decision-maker (runs things, decides, talks to people).

Read first: [`docs/project-summary.md`](docs/project-summary.md) (the whole project in one page) and the end of [`lab-log.md`](lab-log.md).

## Where things live

| Path | What |
| --- | --- |
| `docs/roadmap.md` | Milestones and features, with status. **Check the current milestone before starting work** |
| `docs/session-kickoff.md` | How to start a new session without re-pasting context |
| `docs/decisions/` | One file per decision (options → lean → Ammad's call + why) |
| `docs/engineering-standards.md` | Coding and engineering rules. **Follow them for all code** |
| `docs/runner-tasks.md` | The runner's work queue. Every task for Israr's machine is written here (never pasted in chat); the runner reports back via `report.md` in its run folder |
| `docs/design/` | Design docs; `checker-v0.md` is the M4 build plan and Study A's fixed injection table |
| `docs/outreach/` | `collider-bench-findings.md`: benchmark problems to report. **Read it before any contact with the Collider-Bench authors; add to it when you find one** |
| `docs/artifacts/` | Read-only exports of the claude.ai docs (see `docs/INDEX.md`). Never edit |
| `papers/` | `papers.yaml` manifest + our notes; PDFs in `papers/pdf/` (git-ignored, `python scripts/fetch_papers.py`) |
| `external/collider-bench/` | Collider-Bench as a pinned git submodule. **Never edit** |
| `src/trustlayer/` | All checker code: `ledger`, `checks`, `gate`, `inject`, `report` |
| `tests/` | Unit tests mirroring `src/` |
| `integration/` | How the checker bolts into Collider-Bench (hook config, container mount, attachment points) |
| `tasks/<task-id>/` | Per-task reference material and hand-filled correct ledgers (public sources only) |
| `experiments/NN-name/` | One folder per experiment: README, config, `runs/`, `results/` |
| `frontend/` | Plain-HTML explainers and (later) results pages; open in a browser, no build |
| `scripts/` | Helper scripts (fetch papers, create a run folder) |

The claude.ai docs listed in `docs/INDEX.md` are Claude Docs and can be read directly with the Claude Docs connector, even when they haven't been exported.

## Working rules

1. **Start from the plan, end with a log line.** Each session ends with one line in `lab-log.md`: date · what ran · what we learned · next step.
2. **One measured thing per week.** Nothing new gets built until the current piece has a number.
3. **Every claim gets a number or a source.**
4. **Claude advises, Ammad decides.** Give the options and a lean; Ammad picks and writes one line on why → `docs/decisions/`.
5. **Scope guard.** Phase 1 is the normalization checker only. Recalculation, provenance and human escalation wait.
6. **Label errors with sub-gap codes** 1a–1e, 2a–2e, 3a–3f (defined in `docs/project-summary.md`).

## Fairness and separation (do not break)

- **Two different Claudes.** `.claude/` and this file are for the *builder*. The *test-subject* agent that Collider-Bench launches in the container gets only what `integration/` gives it: the ledger CLI and the gate hook.
- **Never** mount or copy into the container this repo's `CLAUDE.md`, `.claude/`, `docs/`, `papers/notes/` or `tasks/` (the hand-filled ledgers are effectively answer keys). Doing so contaminates Study B.
- **The checker may only use what the agent can see:** the paper, Prospino, HEPData. It never reads Collider-Bench's hidden answers. `tests/test_fairness.py` guards this.

## Two machines

- **Edit code only on Ammad's Windows laptop.** Push to GitHub, pull on the runner, run.
- **The runner (friend's Linux laptop) commits only under `experiments/*/runs/`.** Code and run data never touch the same files.
- Pin every measured run: Collider-Bench commit, container image digest, model snapshot ID, hardware, N_gen (all in the run's `manifest.yaml`). Tag the repo before a measured experiment starts (e.g. `study-b-v1`).

## How to report back (always)

When a piece of work is done, end with a short plain-words summary, nothing longer:

- 2–5 bullets, each one or two lines, saying **what was done** in simple words.
- One bullet for **what's not done, not verified, or needs Ammad's call**, if anything.
- No long reports, no tables, no repeating what was asked. Details go in the files, not the reply.
