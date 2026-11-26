# R5 smoke, attempt 2: **pass** → tag `study-b-v1`

Haiku 4.5, checker arm, sus-16-034_sim-TChiWZ, 02:12–02:22 PKT 27 Nov (0.122 h), token login, $0 on the subscription (API-equivalent $0.90). Launched with the venv on PATH (fix for attempt 1, see `../20261127-0201_study-b-smoke/report.md`).

Checks (R5 step 5–6):
- `outcome: scored` ✓ · `mcp_servers: []` ✓ · gate: 1 bounce, final pass, `tampered: false`, `gate_error: false` ✓
- `checker_time` filled (22.0 s, 11 record-quantity calls) ✓ · `score` filled (δ_norm 1.00, pass false) ✓
- `judge`: `provenance_status: VERIFIED`, overrule NONE, judge model claude-opus-4-6 ✓
- Israr's own login still works (`claude -p "Reply … OK" --model claude-haiku-4-5` → `OK`) ✓. This session stayed busy during the run, and nothing clashed.

Odd, for the record only: the judge's trajectory text mentions a "hallucinated cross section" yet its provenance status is VERIFIED. That's worth a look when labelling (R8). `n_gen: null` in the manifest; R5 doesn't check it.
