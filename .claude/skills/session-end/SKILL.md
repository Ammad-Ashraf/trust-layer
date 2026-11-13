---
name: session-end
description: Close a work session — append the lab-log line, update the roadmap, record any decisions, and give Ammad a short plain-words summary. Use at the end of every session or when Ammad says "wrap up", "let's stop", or "log it".
---

# Session end

1. **Lab log:** append one line to `lab-log.md`:
   `- **YYYY-MM-DD** · what ran · what we learned · next step.`
2. **Roadmap:** update statuses (⬜ 🟨 ✅ ⏸) and tick finished items in `docs/roadmap.md`.
3. **Decisions:** if Ammad made a call this session, add or update a file in `docs/decisions/` (copy `0000-template.md`), including Ammad's one line on why, and update the table in `docs/decisions/README.md`.
4. **Carry back:** note anything durable the claude.ai docs should get (a finding, a decision, a changed date).
5. If code changed, confirm the definition of done in `docs/engineering-standards.md` (ruff, mypy, pytest).

Then reply with the summary, and nothing more:

- 2–5 bullets, one or two lines each, in simple words: what was done.
- One bullet: what's not done, not verified, or needs Ammad's call.
- One bullet: what to carry back to claude.ai, if anything.
