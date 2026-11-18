# Lab log

One line per session: date · what ran · what we learned · next step. Newest at the bottom.

- **2026-11-13** · Read all six claude.ai docs and wrote the project summary; scaffolded the repo (layout, CLAUDE.md, engineering standards, roadmap, decisions, skills, Collider-Bench submodule). · Learned: the claude.ai docs can be read directly via the Docs connector, so manual export is optional. · Next: connect to the runner laptop and do the smoke run on sus-16-034.
- **2026-11-18** · Smoke run on the runner (T5Wg, Sonnet 4.6, OAuth, no checker): ran end to end in 28 min for $5.68 API-equivalent, δ_norm 0.98 (fail); merged the run record and mapped all four attachment points. · Learned: the failure was ε (0.93% vs ~38.6%), with σ, L and units right, so C1–C5 would have passed it; a Stop hook fires in the container and its message reaches the agent; the agent-folder `bin/` is the clean route for `record-quantity`. · Next: Ammad decides 0008–0013; start M2 (fill the sus-16-034 ledger by hand).
