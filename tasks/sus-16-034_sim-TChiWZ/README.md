# sus-16-034_sim-TChiWZ

- **Collider-Bench task:** `sus-16-034_sim-TChiWZ` (task card: `external/collider-bench/ColliderBench/tasks/sus-16-034_sim-TChiWZ/TASK.md`). Difficulty "easy", tolerance 5%, scored on shape and normalization.
- **Signal model:** `TChiWZ_550_200`, meaning pp → χ̃±₁ χ̃⁰₂, with χ̃±₁ → W χ̃⁰₁ and χ̃⁰₂ → Z χ̃⁰₁. Masses: m(χ̃±₁) = m(χ̃⁰₂) = 550 GeV, m(χ̃⁰₁) = 200 GeV.
- **Signal region:** the electroweak on-Z "VZ" region (paper Sec. 5, Table 1), binned in E_T^miss: 100–150, 150–250, 250–350, >350 GeV.
- **Data:** CMS 2016, 35.9 fb⁻¹ at 13 TeV.
- **Paper's per-task results (Collider-Bench Tables 2–3):** Opus 4.7 total/shape error 0.19/0.09, Sonnet 4.6 0.30/0.07. There is a counting gap, so the task is a good fit (decision 0014).

`ledger.yaml` is the hand-filled correct normalization record (milestone M2; also used in Study A).

## Public sources

| What | Where |
| --- | --- |
| Paper | CMS-SUS-16-034, arXiv:1709.08908 (JHEP, doi:10.1007/s13130-018-7845-2 as printed on the paper). Local copy: `external/collider-bench/ColliderBench/tasks/shared/CMS-SUS-16-034/paper/CMS-SUS-16-034.pdf` |
| CMS public page (extra figures and tables) | https://cms-results.web.cern.ch/cms-results/public-results/publications/SUS-16-034/index.html |
| Signal cut flow for this exact benchmark | "Additional Table 7" on that page: `CMS-SUS-16-034_Table-aux_007.pdf` |
| Cross section (NLO+NLL, Resummino) | LHC SUSY Cross Section WG, wino N2C1± at 13 TeV: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections13TeVn2x1wino |
| HEPData | https://www.hepdata.net/record/ins1625745 (INSPIRE 1625745). It shows a bot check to scripts, so open it in your own browser |

Never use `external/collider-bench/ColliderBench/tasks/shared/*/reference/`. Those are the benchmark's hidden answers.

## How to fill the ledger (guide for Ammad)

**The picture.** A fishing trip. σ is how many fish of this kind swim through each square metre of lake. L is how much lake you dragged the net through. BR is the share of those fish that have the colour you're looking for. ε is the share of those that your net actually holds. Multiply them and you get the expected catch:

N = σ × L × BR × ε

The checker is a spell-checker for that sum. It doesn't go fishing again. It checks that every number has a unit and a source, that no factor is missing, and that the numbers you wrote down are the ones you used.

Fill one factor at a time. For each one, write the value, the unit, the exact source (document plus table or page), and one line in your own words.

1. **`signal_model`**: what is being made, and at what masses. Look at the task card's "Definitions" section and Fig. 1 (upper right) of the paper.
2. **`cross_section` (σ)**: how often the collider makes this pair. Look up the 550 GeV row in the SUSY Cross Section WG table. Watch the unit (the table uses fb; Prospino gives pb, and 1 pb = 1000 fb). Paper Sec. 4 says signals are normalised at NLO+NLL, so this is the right table. Also note the ± uncertainty.
3. **`luminosity` (L)**: already filled. Add the exact place in the paper where 35.9 fb⁻¹ is stated (the abstract).
4. **`branching_fraction` (BR)**: the share of events that decay into the final state being counted. This is the tricky one, because it depends on a **convention**, i.e. what you put in BR and what you leave in ε. In this model the chargino always goes to W and the neutralino always goes to Z (100% each). But CMS only counts events where the Z decays to a lepton pair. Additional Table 7's caption states the Z→leptons fraction CMS used. Write down which decays the BR covers, in the `notes` line.
5. **`efficiency` (ε)**: the share of those events that pass every cut of the VZ region. Additional Table 7 gives events after each cut. ε = (events in the region with E_T^miss > 100 GeV) ÷ ("Expected events" at the top). The table's per-bin numbers come from the differences between the E_T^miss rows. Put them in `notes` if you like.
6. **`expected_events`**: multiply the four factors.

**Self-check.** σ × L × BR should come out close to the "Expected events" number at the top of Additional Table 7. The full product should come out close to its E_T^miss > 100 GeV row. If either is off by about ×1000 or ×10, a unit or a BR is wrong. Those are exactly the mistakes the checker is built to catch (sub-gaps 1a and 1c).

**Done when** (roadmap M2): every value has a unit and a source, and you can explain each factor in one plain sentence.
