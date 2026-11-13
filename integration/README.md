# Integration with Collider-Bench

How the checker bolts onto Collider-Bench without changing the benchmark. The submodule in `external/collider-bench/` is never edited; everything we add lives here.

| Path | What |
| --- | --- |
| `attachment-points.md` | The four places the checker connects, mapped during the smoke run |
| `subject-claude/` | Settings given to the **test-subject** agent: the Stop-hook gate config. Nothing else |
| `container/` | How the ledger CLI and gate get into the container (mount or overlay) and onto the agent's PATH |

**Rule:** the container receives only the ledger CLI and the gate hook. Never this repo's `CLAUDE.md`, `.claude/`, `docs/`, `papers/notes/` or `tasks/`.
