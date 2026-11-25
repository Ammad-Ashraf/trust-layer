# Checker v0: design and build plan (M4, then Study A)

Written 2026-11-26 by Claude (research lead), after closing M3. This is the plan we build against. When the build changes a choice here, update this file in the same commit.

**Goal of M4 (roadmap):** C1–C5 pass unit tests, and the gate blocks a bad ledger in a real test run.
**What M4 feeds:** Study A (M5) runs the same checks on hand-filled ledgers with injected errors, so the checker and Study A share one ledger format. That's the main design constraint.

## 1. What M3 taught us, and what it changes

The smoke run made zero counting (Gap 1) errors: σ, L, BR, units and carry-through were all right. Its failure came from the detector setup (labels L1–L5 in `experiments/00-smoke-run/runs/.../labels.yaml`). So:

- **The checker would have passed that run, correctly.** C1–C5 are not designed to catch ε or detector errors, and we won't claim they do. Phase 1's claim stays narrow: "it catches counting errors" (Study A), and "does it change real outcomes" (Study B).
- **The gate checks only the end state.** In that run the agent decided on a fix and then lost it when its context was compacted (L5). A Stop hook that reads the final ledger and the final results file is immune to that.
- **ε needs its provenance in the ledger.** Not just "ε = 0.0093" but how it was made (passing events, generated events, the script). Then C3 and C5 can test it, and a human reading the ledger sees the 93/10,000 at a glance.
- **A benchmark-level finding for the Collider-Bench authors** (logged as F1 in [`docs/outreach/collider-bench-findings.md`](../outreach/collider-bench-findings.md)): the agent cheat-sheet points every agent at the stock Delphes CMS card, which doesn't treat the gravitino as invisible. Every gravitino task (T5Wg, TChiWg) inherits that trap.
- **A Study B caveat:** on T5Wg, the gravitino trap may swamp any counting error, so the checker arm can't win there. Recheck the task choice when Study B starts (with 0005–0007).

## 2. The pieces

```
agent (in container)                     checker (same container, read-only mount)
  │  bin/record-quantity ... ───────────▶ ledger.yaml   (workspace/, agent-writable)
  │  fills results/*.yaml  ─────────────▶ submission
  │  tries to stop
  ▼
Stop hook ──▶ trustlayer.gate ──▶ checks C1..C5 (pure functions)
                 │                 inputs: ledger + task context + submission
                 ├─ all pass ─────▶ exit 0 (agent may stop)
                 ├─ fail, bounce < 3 ▶ exit 2 + message (absolute paths) → agent fixes
                 └─ fail, bounce = 3 ▶ exit 0, "submitted with warnings"
                 every decision → bounce log (outside the workspace)
```

| Component | Path | Runs where |
| --- | --- | --- |
| Ledger (schema, units, load/save) | `src/trustlayer/ledger/` | container + host |
| `record-quantity` CLI | `src/trustlayer/ledger/cli.py` | container |
| Checks C1–C5 + registry | `src/trustlayer/checks/` | container + host (Study A) |
| Gate (Stop hook entry point) | `src/trustlayer/gate/` | container |
| Task context (public facts per task) | `integration/task-context/<task>.yaml` | mounted read-only |
| Agent folder `simple_ledger` | our Collider-Bench fork (0008) | built by `scripts/build_agent_folder.py` |
| Injector | `src/trustlayer/inject/` | host (Study A) |
| Report | `src/trustlayer/report/` | host |

## 3. The ledger

**One schema for both uses:** the agent's ledger in the container, and the hand-filled ledgers in `tasks/`. It's the format the sus-16-034 ledger already uses, plus a few fields. Versioned with `schema_version`. The current hand ledgers are version 1; this is version 2, and the loader reads both.

```yaml
schema_version: 2
task: sus-16-034_sim-TChiWZ
quantities:
  cross_section:
    value: 30.1656
    unit: fb
    source: "LHC SUSY xsec WG, wino C1N2 NLO+NLL, m = 550 GeV"
    source_type: xsec_wg          # prospino | xsec_wg | paper | hepdata | generator | other
    process: chargino_neutralino  # canonical token, see task context
    masses_gev: {chargino_1: 550, neutralino_2: 550, neutralino_1: 200}
  luminosity:     {value: 35.9, unit: fb^-1, source: "paper abstract", source_type: paper}
  branching_fraction:
    value: 0.101
    unit: dimensionless
    source: "PDG, Z -> ll (e, mu, tau)"
    source_type: other
    reason: null                  # required when value is exactly 1 ("decays are in the simulation")
  efficiency:
    value: 0.0495
    unit: dimensionless
    source: "analysis.py cut flow"
    n_pass: 495                   # optional but encouraged: weighted or raw passing events
    n_gen: 10000                  # generated events the efficiency is relative to
  corrections:                    # optional extra factors: trigger, scale factors
    - {name: trigger, value: 0.943, unit: dimensionless, source: "paper Sec. 4"}
expected_events: {value: 5.41, unit: events}   # optional; the checker recomputes it anyway
```

**Units (decision 0009, no `pint` in the container):** a fixed table in `ledger/units.py`. Each unit maps to a scale to fb and an "area power": `fb` (1, +1), `pb` (1000, +1), `fb^-1` (1, −1), `pb^-1` (0.001, −1), `dimensionless` (1, 0). A product is unit-free only when the area powers sum to 0. Unknown unit strings are an error, not a guess. `pint` stays a host-side dev dependency for cross-checking the table in tests. `docs/engineering-standards.md` is updated to match (its rule still says "pint everywhere").

**`record-quantity` CLI** (what the agent calls):

```
bin/record-quantity cross_section --value 3.96 --unit fb --source "bin/prospino gg NLO" \
    --source-type prospino --process gluino_pair --mass gluino=1750
bin/record-quantity efficiency --value 0.0093 --n-pass 93 --n-gen 10000 --source "analysis.py"
bin/record-quantity show        # prints the ledger and the product sigma*L*BR*eps*corrections
```

- It writes `ledger.yaml` in the working directory. The write is atomic (temp file, then rename), and the last value wins.
- It validates units and value ranges at the moment of entry and refuses bad input with a one-line reason. The checks still re-run everything at the end.
- `show` is the agent's own view of the formula. It gives answers about the agent's own numbers only, never a reference.

## 4. The checks

One interface (engineering standards §3):

```python
def check(inputs: CheckInputs) -> CheckResult
# CheckInputs: ledger, task (TaskContext), submission (+ submission_error), ledger_path, c5_tolerance
CheckResult(check_id="C1", subgap="1a", passed=bool, messages=(...))
```

The gate runs a registered list and knows nothing about individual checks. `TaskContext` comes from `integration/task-context/<task>.yaml`, built **only from the public task card** (TASK.md: benchmark name, masses, luminosity, process family). It holds nothing the agent can't read itself, so it may be mounted.

| Check | Guards | Passes when | Fails on (examples) |
| --- | --- | --- | --- |
| C1 Units | 1a | σ has area power +1, L has −1, BR/ε/corrections are dimensionless, and the full product is unit-free; every unit is in the table | `unit: pb` on L; a missing unit; σ in "events" |
| C2 Source | 1b | σ `source_type` ∈ {prospino, xsec_wg, paper}; if a generator σ is recorded, σ isn't within 1% of it; **and (0017) a `prospino` σ matches, within 1%, the NLO value of a Prospino run found in this run's scratch folders** | `source_type: generator`; σ equals the MadGraph LO value |
| C3 Complete | 1c | σ, L, BR, ε are all present with values; 0 < BR ≤ 1 and 0 < ε ≤ 1; BR = 1 or ε = 1 only with a non-empty `reason`; if n_pass/n_gen are given, they agree with ε within 1% | BR missing; BR = 1 with no reason; ε = 1.3 |
| C4 Match | 1d | σ `process` and `masses_gev` equal the task context; L equals the task's luminosity | σ for a 500 GeV point on a 550 GeV task; L = 36.1 |
| C5 Carried through | 1e | the submitted bins exist and are all filled, and their sum equals σ·L·BR·ε·corrections within the tolerance τ | the sum is 100× the ledger; no ledger at all (agent skipped it); null bins |

**Tolerance τ for C5** lives in config (`experiments/02-study-a/config.yaml`), not in code. It is fixed before Study A runs (see §7), never tuned on Study A's own results.

**Fail loudly:** a check that can't run (unreadable file, unknown task) returns a failing result that names what's missing. It never returns a silent pass.

## 5. The gate

- **Entry point:** `python -m trustlayer.gate`, called by a Claude Code **Stop hook** in the checker-arm workspace's project settings (`workspace/.claude/settings.json`, written by `simple_ledger/run.py`; see `integration/container/README.md`). The host user's settings can't be used, because the harness copies them into baseline runs too. It reads the hook's JSON on stdin (it uses `cwd`; `stop_hook_active` is logged).
- **Finding the inputs:** the ledger at `<cwd>/ledger.yaml`, the submission at `<cwd>/results/*.yaml` (the two-document template), and the task context from the path in the `TRUSTLAYER_TASK_CONTEXT` env var, set by the agent folder's launcher.
- **Decision:**
  - all checks pass → exit 0;
  - otherwise, while fewer than 3 bounces have happened → exit 2 with a message on stderr;
  - at the 3rd → exit 0 and log `submitted_with_warnings`.
- **Messages** use absolute paths (attachment point 2) and the agent's own numbers. For example: `C5: your ledger gives 5.41 events (σ·L·BR·ε), but /abs/.../results/histogram.yaml sums to 0.0541 (100× smaller). Fix whichever is wrong, then stop again.`
- **Bounce log:** JSON lines at `$HOME/.trustlayer/bounces.jsonl`. That's the fake home, outside the workspace (attachment point 2). Each entry records the time, bounce number, failing checks and message hash. The runner copies the log into the run folder after the run.
- **Tamper guard (runner side, after the run):** hash the subject's `settings.json` and the hook script before and after. A mismatch marks the run `tampered` in `manifest.yaml`.

## 6. Getting it into the container

Decision 0008 is a fork of Collider-Bench plus one agent folder, `agents/simple_ledger/`. It is named with an underscore because Collider-Bench imports `agents.<name>.run` as a Python module. The folder is

- a copy of `agents/simple/`;
- plus `runtime/bin/record-quantity`, a small bash shim that runs `/opt/conda/envs/lhc_analysis/bin/python -m trustlayer.ledger.cli` with `PYTHONPATH` set to `runtime/lib/`;
- plus `runtime/lib/trustlayer/`, the checker source copied in by `scripts/build_agent_folder.py`, so one fork commit pins exactly what the agent ran;
- plus `runtime/task-context/` (the public task facts from §4);
- plus one paragraph in its `AGENTS.md`: "record σ, L, BR, ε with `bin/record-quantity`; a checker reads the ledger when you finish".

The baseline arm keeps upstream `simple` untouched.

Never copied in: `tasks/`, `docs/`, `CLAUDE.md`, `.claude/`, `papers/notes/`. `tests/test_fairness.py` is extended so that the build script's output is scanned and fails on any of those paths or on ledger answer values.

## 7. Study A: fixed before it runs

To keep Study A from being a test we designed to pass, its injection list and tolerance are written down and committed **before the checks are built**. **Fixed by decision 0016 (option A, 2026-11-26).** Don't edit this table; any later addition goes below it, marked "added after".

| Sub-gap | Injection (one per broken copy) | Grounded in |
| --- | --- | --- |
| 1a | σ value in pb but unit says fb (×1000); and L entered in pb⁻¹ unconverted | Ammad's own M2 slip (fb vs pb) |
| 1b | σ replaced by the generator's LO value with `source_type: generator`; and the same value with a false `prospino` label | Collider-Bench paper failure mode; smoke run's σ_LO = 1.453 fb vs 3.96 fb |
| 1c | BR removed; and BR = 1 with no reason | Collider-Bench paper; M2 |
| 1d | σ taken at a neighbouring mass point (550 → 500 GeV); and L = 36.1 | Ammad's M2 slip (550 → 500) |
| 1e | submitted bins left at an earlier value (not rescaled); and one bin left null | smoke run L5 shows how a fix gets lost |
| clean | the correct ledger, plus near-misses that must **pass**: σ in pb converted correctly; BR = 1 with a valid reason; BR 0.10 vs 0.101 (1%, below τ) | false-alarm rate |

**Added after 0016 (decision 0017, 2026-11-26), reported separately:**

| Sub-gap | Injection | Grounded in |
| --- | --- | --- |
| 1b / 2a | σ labelled `prospino` with no Prospino output in the run; and labelled `prospino` but matching none of the run's Prospino results | R2 (Haiku): an invented 0.15 fb labelled Prospino |

- **Measured:** catch rate per sub-gap, and false-alarm rate on clean and near-miss copies, for 3 tasks.
- **Proposed τ = 5%:** above the honest rounding seen in M2 (0.03–1%), and far below the smallest injected error (×1.5 at a neighbouring mass point).
- **Tasks:** sus-16-034 (ledger done); T5Wg and the T2tt task (both ledgers still to fill, from public sources only).

## 8. Build order and tests

Each step ends with tests passing and one commit (engineering standards' definition of done).

| # | Step | Done when | Size |
| --- | --- | --- | --- |
| 1 | Decision 0016: Study A injections + τ (§7) | committed, Ammad's line written | small |
| 2 | `ledger`: schema v2, units table, load/save (reads v1), validation | round-trips both existing ledgers; the unit table matches `pint` in a test | ½ day |
| 3 | `record-quantity` CLI incl. `show` | CLI tests on a temp workspace | ½ day |
| 4 | C1–C5 + registry, tests first | each check has a correct case, each failure it guards, and edge cases; sus-16-034 ledger passes all five | 1–2 days |
| 5 | `gate`: Stop-hook entry, bounce cap, log, messages | tests feed hook JSON on stdin and assert exit codes, messages and log lines | 1 day |
| 6 | `build_agent_folder.py` + fork + `AGENTS.md` paragraph; extend the fairness test | fork commit pinned in the submodule; fairness test scans the built folder | ½ day |
| 7 | Container gate test (no API cost): run the gate inside the image on a bad and a good workspace | exit 2 then 0, as expected | runner, 1 h |
| 8 | One real cheap run (Haiku 4.5, OAuth, about $1) with `simple_ledger` | gate fired at least once, the agent saw the message, the bounce log was committed → **M4 done** | runner, 1 h |

Then M5: `inject` + `report`, fill the two missing hand ledgers, run Study A.

## 8a. Build status (2026-11-26)

Steps 2–6 are built and tested on the dev laptop: 161 tests, ruff and mypy clean. Every Study A injection is caught by exactly the checks listed in `tests/checks/test_study_a_injections.py`, with no false alarm on the near-misses. Which check catches which injection:

| Injection | Caught by |
| --- | --- |
| 1a σ in pb written as fb | C5 (×1000 off); C1 can't see a value whose unit label is valid |
| 1a L in pb⁻¹ unconverted | C4, C5 |
| 1b LO σ (labelled generator, or falsely labelled prospino with the generator σ recorded) | C2, C5 |
| 1c BR removed / BR = 1 without reason | C3, C5 |
| 1d neighbouring mass point | C4, C5 |
| 1d L = 36.1 | C4 (C5 stays within τ) |
| 1e bins unscaled / null bin | C5 |

So C1 catches only missing or wrong-kind units. A unit that is valid but wrong for its value is caught downstream by C4 or C5. Study A reports catches per check, so this is visible, not hidden. Steps 7–8 run on the runner (`integration/container/README.md`).

## 9. Risks

- **The agent ignores the ledger.** C5 fails with "no ledger", the gate bounces, and after 3 bounces the run submits with warnings, which is itself a measured outcome.
- **The agent edits the ledger to match its bins without fixing the physics.** C2–C4 still test the recorded σ, L and BR against the source rules and the task facts. A consistent but wrong ε is out of scope (3c, parked).
- **The checker becomes a coaching channel.** Messages quote only the agent's own numbers and rule names, never reference values. The fairness test guards the code side.
- **Hook tampering.** See the tamper guard in §5.
- **Study A circularity.** That's why §7 is fixed and grounded in observed slips before the checks exist.
