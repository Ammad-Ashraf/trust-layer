# Central Documentation Index — Trust Layer for AI Science

Last updated: 13 Nov 2026 · Maintained in the "AI Agents in Particle Physics" claude.ai project.

## How this works

- The **claude.ai artifacts are the source of truth** — Ammad and Claude (chat) edit, review and discuss there.
- **Claude Code can read these docs directly** through the Claude Docs connector (confirmed 13 Nov 2026), so export is optional. When an offline copy is useful, Ammad exports the artifact (Markdown export from the artifact page) into `docs/artifacts/` under the filename in the table. Claude Code reads exported files as **read-only context** — it never edits them.
- **Re-sync strategy:**
  1. When an artifact changes in claude.ai → Ammad re-exports it to the same filename (overwrite) and updates its "Exported" date below.
  2. When Claude Code produces a durable finding or decision → it goes in `lab-log.md` first; Ammad carries it to the chat session, the artifact gets updated there, then re-exported (step 1).
  3. When a new artifact is created → add a row here, and export it only if Claude Code needs it for development.
  4. If an exported file and this table disagree on dates, trust the artifact and re-export.

## Documents

| Doc | Export to (filename in docs/) | Artifact (source of truth) | Last artifact update | Exported |
| --- | --- | --- | --- | --- |
| Execution Plan: Trust Layer Phase 1 — the working plan: studies, checker v0 design, gate guards, compute plan, timeline, this week's checklist | `execution-plan-phase-1.md` | https://claude.ai/artifact/MhydmMD2naJ4h5cn7a6wkA | 13 Nov 2026 | — |
| Review: Pipeline & Research Approach (13 Nov 2026) — reasoning behind the 13 Nov plan changes | `review-2026-11-13-pipeline-research.md` | https://claude.ai/artifact/HmDUBUEtgRatJ5rAdtw8qq | 13 Nov 2026 | — |
| Research Gaps: AI Agents in Particle Physics — Gap 1/2/3 with sub-gap codes 1a–3f (use these codes when labelling errors) | `research-gaps.md` | https://claude.ai/code/artifact/0175bff2-5e98-475c-8bf2-dfda744de1df | 19 Oct 2026 | — |
| Foundation Papers and Gap Map — the 8 anchor papers + related work (Ariadne, Ravel, ColliderAgent added 13 Nov) | `foundation-papers-and-gap-map.md` | https://claude.ai/code/artifact/5a8e1566-c035-4a2d-95f9-29c4768a6648 | 13 Nov 2026 | — |
| Product Vision: Trust Layer for AI Science — problem, the 4 parts, roadmap, outreach | `product-vision-trust-layer.md` | https://claude.ai/code/artifact/eb2bfb26-b3dc-4726-bc2b-d7ea2134987d | 19 Oct 2026 | — |
| How an LHC Analysis Works, and Where Our Work Fits — the 7 stages, recasting, gaps on the journey | `lhc-analysis-process.md` | https://claude.ai/artifact/Dk6V9gHZfsdhdwjoEEAGVJ | 11 Nov 2026 | — |

Fill the "Exported" column with the date each file is placed/refreshed in this folder.

## Not exported (live only in the claude.ai project)

- Session summaries (`claude/chat-discussion-sessions/…`) — chat-to-chat handoff notes.
- Application goals and story bank — Master's/scholarship material, not needed for development.

## Local-only files (created by development, never exported from artifacts)

| File | Purpose |
| --- | --- |
| `lab-log.md` (repo root) | One line per session: what was measured or decided. Required by the working rules. |
| `CLAUDE.md` (repo root, optional) | Auto-loaded context for Claude Code — points here and states the working rules. |
