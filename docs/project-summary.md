# Project Summary — Trust Layer for AI Science (Claude Code's understanding)

Written 13 Nov 2026 by Claude Code, after reading `docs/INDEX.md` and all six claude.ai docs it lists (read live through the Claude Docs connector, not from exports, because none had been exported yet). This is my reading of the project, not a source of truth: the claude.ai docs stay authoritative.

---

## 1. The project in one paragraph

AI agents can already run particle-physics analyses, but their numbers can be silently wrong. The long-term goal is a **trust layer**: a verification layer that sits beside any AI agent doing quantitative science and checks each number before it is reported. Particle physics is the proving ground because the counting math is hard and public answer keys exist (Collider-Bench). The near-term goal is narrow: **Phase 1 builds and measures a normalization checker** on Collider-Bench, with a measured result by **15 Jan 2027** for the **CERN openlab Summer Student Programme application (closes 21 Jan 2027, 23:59 Geneva)**. The same work feeds ETH/EPFL and Erasmus Mundus Master's applications (Fall 2027) and a spring-2027 preprint.

## 2. The physics I need to get right

**The normalization formula** that turns simulated events into an expected count:

```
expected events = cross-section (σ) × luminosity (L) × decay chance (BR) × efficiency (ε)
```

| Quantity | Meaning | Unit |
| --- | --- | --- |
| Cross-section σ | How likely a process is | pb or fb (1 pb = 1,000 fb) |
| Luminosity L | How much data was collected | fb⁻¹ (Collider-Bench tasks use **35.9 fb⁻¹**, CMS 2016 data) |
| Branching fraction BR | Share of particles decaying the counted way | unitless |
| Efficiency ε | Share of events surviving detector + cuts | unitless |

σ (fb) × L (fb⁻¹) is unit-free: the area units cancel. Worked example used throughout the docs: 10 fb × 35.9 fb⁻¹ = 359 → × 0.5 BR = 180 → × 0.1 ε = **18 events**.

**How Collider-Bench works** ([arXiv 2605.13950](https://arxiv.org/html/2605.13950v1), [repo](https://github.com/dfaroughy/Collider-Bench)): an agent rebuilds an already-published CMS search (*recasting*) from the paper, using simulated events: read paper → MadGraph (generate) → Pythia (shower/decay) → Delphes (fast detector) → own event selection → **normalize (Gap 1 lives here)** → fill a YAML results file graded against hidden answers. Paper setup: 128 AMD EPYC cores per agent, 2.5 h wall-clock budget per task, the agent picks its own event count N_gen.

**Target tasks:** sus-16-034 (TChiWZ), sus-16-046 (T5Wg), sus-16-051 (T2tt). They still have to be checked against the paper's per-task tables before we commit to them (see §5).

In the 7-stage LHC analysis lifecycle (collect → calibrate/reconstruct → select → background → blinded statistics → internal review → publish), Collider-Bench covers stages 2–5, and our checker sits at normalization (end of stage 3). The checker is **blind by design**: it never needs the signal region, which helps us sell it to physicists.

## 3. The gaps (use these codes when labelling errors)

From Collider-Bench's findings:

- **Gap 1: counting math wrong** (Phase 1 target). Shapes mostly right, totals often wrong.
  - **1a** wrong units (pb↔fb, 1,000×) · **1b** wrong source (LO generator σ instead of NLO/Prospino) · **1c** missing factor (BR forgotten) · **1d** mismatched input (wrong mass point/process) · **1e** lost along the way (right value computed, never used)
- **Gap 2: fabricated answers.** About 6% of 364 judged runs, mostly in cheap models (Haiku 4.5, DeepSeek-V4, GPT-5.4-mini).
  - **2a** hard-coded numbers · **2b** fake simulator · **2c** made-up efficiencies · **2d** copying the paper (the AI version of breaking blinding) · **2e** stale result submitted
- **Gap 3: AI alone is worse than AI + physicist.** The bottleneck is judgment, not coding.
  - **3a** filling missing details · **3b** choosing conventions · **3c** sanity checks · **3d** diagnosing mismatches · **3e** approximations · **3f** consistency across similar tasks

## 4. The four-part trust layer (vision) and where Phase 1 sits

| Part | Targets | Status |
| --- | --- | --- |
| Unit tracking / normalization checker | 1a–1e | **Phase 1: building now** |
| Second-opinion recalculation | 1b, 1c, 1d, 3c | Parking lot |
| Provenance check | 2a–2e | Parking lot (leading Phase 2 candidate: cheap to test, Collider-Bench's judge labels fabrication) |
| Human escalation | 3a, 3b, 3d, 3e | Parking lot |

Roadmap: **(1) Prove it (research) → gate: measured gain on benchmark → (2) open-source tool, all four parts → gate: used by outside researchers → (3) product** for all quantitative AI science (labs, pharma, AI teams).

## 5. Phase 1 plan (the part I will be building)

**Research question:** does a normalization checker that tracks units and sources reduce Gap-1 errors when an AI agent rebuilds an LHC analysis?
**H1:** with the checker, the same agent has lower normalization error and a higher pass rate, and its shape score is no worse.

**Metrics** (Collider-Bench's own, so nobody can say we picked flattering ones): δ_norm = |Ŷ − Y*| / Y* (median of 3 runs) · pass rate (relative L² < 0.33) · shape score (L² on unit-normalized bins, "no worse") · our own per-sub-gap detection rate · cost/time overhead < 20%. 3 tasks × 3 runs is reported as a **pilot**, with no significance claims.

**Two studies, cheap one first:**
- **Study A: error injection ("fire drill").** Build correct normalization records by hand for the 3 tasks (from the paper, HEPData, Prospino), make broken copies with one known 1a–1e mistake each, and measure catch rate per sub-gap plus false-alarm rate on clean records. Plain Python, no API cost, no simulation. **This is the backbone claim.**
- **Study B: agent ablation.** Same agent/model/tasks, 3 runs each, with vs without checker = 18 runs, scored with Collider-Bench's evaluator + judge, every failure labelled with a sub-gap code.
- **Fairness rule:** the checker only sees what the agent sees (paper, Prospino, HEPData). It never touches the hidden answers.
- **Power risk:** a strong model may make too few baseline normalization errors to show a difference. Mitigations: pick tasks where the chosen model actually failed normalization in the paper's per-task tables, plus an optional Haiku 4.5 arm (about $20). Study A carries the claim either way.

**Checker v0 architecture.** Two parts bolted onto Collider-Bench, with no benchmark changes:

| Check | Sub-gap | Rule |
| --- | --- | --- |
| C1 Units | 1a | Every number has a unit; σ × L must come out unit-free; pb↔fb converted explicitly |
| C2 Source | 1b | σ comes from Prospino (NLO) or the paper, not raw MadGraph LO |
| C3 Complete formula | 1c | Every factor σ × L × BR × ε is recorded, or marked "= 1" with a reason |
| C4 Match | 1d | σ process and mass point match the task's signal model |
| C5 Carried through | 1e | Sum of submitted yields matches the ledger's formula within a tolerance set in Study A (also catches an agent that skips the ledger) |

Build order: **`ledger`** (Python package on `pint` with pb/fb/fb⁻¹ and a `record-quantity` CLI the agent calls) → **`checks`** (C1–C5 as plain functions, with unit tests) → **`gate`** (a Claude Code **Stop hook** that runs the checks when the agent tries to finish and returns errors) → **`inject`** (Study A broken copies) → **`report`** (one results table for both studies).

**Gate guards:** max 3 bounces, then submit with warnings · log every bounce (fixed or argued) · report wall-clock and tokens per arm (time-fairness) · record N_gen per run as a visible confounder.
**Pin everything:** container image digest, Collider-Bench commit, model snapshot ID, identical hardware across arms.
**Decided: gate, not advisory tool**, so every run gets the same treatment.

**Timeline** (from the plan's chart):

| Workstream | Dates | Done when |
| --- | --- | --- |
| Set up repo + container | 11–17 Nov | One task runs end to end; lab log started |
| Learn formula by hand | 16–29 Nov | Ammad can fill the sus-16-034 ledger with every unit and source |
| Baseline run, label errors | 23 Nov–6 Dec | One full transcript read; every mistake coded |
| Build checker v0 | 30 Nov–15 Dec | C1–C5 pass unit tests; gate blocks a bad ledger in a test run |
| Study A | 9–22 Dec | Catch rate per sub-gap + false-alarm rate, 3 tasks |
| Study B (18 runs) | 16 Dec–5 Jan | 18 scored, labelled runs (holidays: run unattended) |
| Note + public repo | 4–15 Jan | 2–4 page note, public repo, one quotable results table |
| CERN openlab deadline | **21 Jan 2027** | |
| Send results to Collider-Bench authors | 25 Jan 2027 | |

**Machine setup (decided 13 Nov):**

| Machine | Job |
| --- | --- |
| Ammad's Windows laptop (this folder, Claude Code Local) | **All development**: ledger, C1–C5, gate, inject, report, Study A. Plain Python, no Linux or simulation needed |
| Friend's 8-core native-Linux laptop (SSH from Claude Desktop; Tailscale if on different networks) | **Only runs things**: smoke run, baseline transcripts, gate tests in real runs |
| Rented 128-vCPU EPYC cloud instance | Study B's 18 measured runs (about 20–25 machine-hours, roughly $50–170, late Dec) |

Rules: edit code only on Ammad's laptop (push → pull → run) · one GitHub repo cloned into `D:\Professional\Particle-Physics` · the test-subject agent inside the container is a separate Claude Code with its own spend-limited API key, revoked after Phase 1 · WSL2 + Docker on Ammad's laptop is the backup · cloud sessions are not used for runs · the GPU doesn't matter (the MadGraph/Pythia/Delphes stack is CPU-only).

**This week's checklist (13–17 Nov):** connect to the friend's laptop → create the GitHub repo and clone it on both machines → clone and build the Collider-Bench container (record digest + commit) → create the spend-limited API key → **smoke run** (sus-16-034, tiny N_gen, cheap model, no checker; record wall-clock, cost, N_gen, setup problems) → start `lab-log.md` → send the compute emails (supervisor, NCP; bonus track) → read the paper's per-task tables for the task choice.

**The smoke run must also map four attachment points** (checker design starts from this map):
1. Where the ledger lives: the agent's workspace dir in the container; `record-quantity` must be on its PATH; the ledger file must be readable by the gate at run end.
2. Where the gate fires: where the harness's Claude Code hook config goes, that a Stop hook actually fires, and that its rejection message reaches the agent.
3. Where run artifacts land: `session.jsonl`, the submitted YAML, the evaluator output.
4. What `bin/run-analysis` activates: the checks must run inside or alongside its conda env.

**Deferred until the smoke run produces real numbers (by about 1 Dec):** Study B model (Opus 4.7, about $255, stronger headline vs Sonnet 4.6, about $137, fits the cap) · budget cap ($300 / raise to about $450 / free NCP or university compute) · Haiku 4.5 arm (about $20).

## 6. Novelty claim and competition

Narrow claim: **the first measured test of an outside normalization checker on Collider-Bench, plus an error-injection suite mapped to sub-gaps 1a–1e.** Closest neighbours: MadAgents.v3 (in-agent self-checks; read in full before claiming), "Reining in an Agentic Harness" and Ravel (designs without measurement), HEPTABench (possible second test bed), PhysVEC (same idea, other field). **Scoop risk:** Ariadne comes from the Collider-Bench group itself (Rutgers), so move fast and aim to be "their collaborator, not their footnote." Re-search arXiv every two weeks and the day before anything goes public.

## 7. Working rules I will follow

- Each session starts from the plan + `lab-log.md` and ends with one log line: date, what ran, what we learned, next step.
- One measured thing per week; nothing new gets built until the current piece has a number.
- Every claim gets a number or a source.
- Claude advises, Ammad decides: options + a lean, Ammad picks and writes one line on why.
- **Scope guard:** Phase 1 is the normalization checker only.
- The `docs/` exports are read-only context. Durable findings go to `lab-log.md` first, and Ammad carries them back to the claude.ai docs.

## 8. Current state of this folder

- Contains only `docs/INDEX.md` (plus this file). It is **not a git repo yet**, and there is no `lab-log.md`, no `CLAUDE.md`, and no code. Every "Exported" cell in the index is still "—".
- As of 13 Nov, nothing from this week's checklist exists locally.

## 9. Things I noticed that you may want to act on

1. **I can read the docs directly.** The index says Claude Code can't open the artifact links, but in this session I read all six through the Claude Docs connector. Manual export is still useful for other sessions or machines, but re-syncing doesn't have to depend on it. Worth updating the "How this works" note in the index.
2. **Unaccepted suggestions in the Execution Plan.** It holds about 15 pending suggestions from 11 Nov: questions and draft notes that never became doc text. Most are superseded by the 13 Nov decisions, but a few are still open:
   - Using the **Claude Pro subscription instead of API credits** for agent runs. A draft table notes that a Pro run can stop at the 5-hour limit mid-task, which ruins that data point.
   - A request for a **small example of why "skipping the ledger doesn't escape the gate"** (C5).
   - A request for a **scheduled routine** that re-searches arXiv and updates a tracking sheet.
   - A **free-compute reality check**: Colab and Kaggle can't run the container; Azure for Students was suggested.
   - Using **Opus 4.7** for Study B, and possibly a newer model for Study A.

   The LHC doc also has one pending note: "I want to understand the units…". Its Units section now covers that.
3. **Small inconsistencies between docs:**
   - The Product Vision (19 Oct) frames the first experiment as "unit tracking alone" and maps 1b/1c/1d to second-opinion recalculation. Checker v0's C2–C4 already cover 1b–1d, so Phase 1 is broader than the vision doc says.
   - The vision doc's budget ($200–260, GPT-5.5) and 7-week plan are superseded by the Execution Plan.
   - The plan's risk table still says "hard cap of $300", while the cap decision is deferred.
   - The plan's "Your calls" still shows a Sonnet 4.6 lean next to the "deferred" note.
4. **The openlab date was flagged as unconfirmed.** It came from a job aggregator. A pending suggestion says Ammad confirmed 21 Jan 2027; worth recording that in the doc itself.
