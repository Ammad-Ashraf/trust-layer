# 0010 — Isolating the test-subject agent's settings

- **Status:** decided
- **Date:** 2026-11-18
- **Decide by:** before M3 baseline runs

## Question

The harness copies the host user's `~/.claude.json` and `~/.claude/settings.json` into the subject agent's home. On the runner, that leaked an MCP server and the claude.ai connectors (disabled by hand for the smoke run). How do we keep the subject clean and also deliver the Stop hook?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. A dedicated runner OS user (e.g. `tlsubject`) whose home holds only the subject's settings, the hook and its login or API key | Clean by construction; no submodule change; also carries the hook | One-time setup on the runner (needs sudo) |
| B. Edit the host user's settings before each run and restore them after | No new user | Error-prone; easy to forget; one mistake contaminates a run |

## Claude's lean

A. It makes fairness a property of the machine, not of remembering a checklist.

## Decision

A, a dedicated `tlsubject` user on the runner. Decided by Claude (delegated): it keeps the subject clean by construction instead of by a checklist. Needs Israr's OK and a sudo command on his laptop.
