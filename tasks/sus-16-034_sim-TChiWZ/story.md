# The golden dolphin story: the sus-16-034 ledger in plain words

A revision sheet for milestone M2. It explains every line of [`ledger.yaml`](ledger.yaml) as one story. It was written from the guided sessions of 18–24 Nov 2026. The animated lessons are in [`frontend/particles.html`](../../frontend/particles.html) and [`frontend/big-picture.html`](../../frontend/big-picture.html).

## The one question

> If this imagined particle existed, how many would CMS have caught in its 2016 data?

Every Collider-Bench task comes down to that one number. The AI predicts it by simulating collisions. Our checker makes sure the arithmetic behind the number is right, like a spell-checker for the sum:

> **catches = σ × L × BR × ε**

## The lake and the buckets

- **The lake** is all the proton collisions CMS recorded in **2016**: about 2.8 million billion of them.
- **One bucket** is a fixed scoop of the lake: **1 fb⁻¹** ("one inverse femtobarn"), about 78 trillion collisions.
- Rain is measured the same way. A weather report says "35 mm of rain fell", not "a billion drops fell", so anyone can work out what landed in their own bucket.

## The what-if story (the signal model)

Supersymmetry is an unproven idea: every normal particle may have a heavier "twin". Our task imagines one fixed story, called `TChiWZ_550_200`. All of it is given by the task card; none of it is measured:

1. Two protons collide (two ordinary waves crash). Once in a long while, the crash **makes** a pair of golden dolphins: dolphin A (the **chargino**) and dolphin B (**neutralino‑2**). Each weighs **550 GeV**.
2. Within a blink, each one drops a normal fish and becomes a lighter twin. There is only **one step** on each side:
   - dolphin A → a **mackerel** (the **W** boson) + a **glass fish** (the lightest neutralino);
   - dolphin B → a **tuna** (the **Z** boson) + a **glass fish**.
3. **Glass fish weigh 200 GeV.** They are heavy, but no net can catch them, so they fly out unseen. We know they were there only because the boat rocks with nothing visible pushing it. That rocking is **missing energy** (E_T^miss).

The task names read like this: **T** = test story · **Chi** = χ, the chargino/neutralino twins · **WZ** = the normal fish they drop · **550** = the heavy twins' weight · **200** = the glass fish's weight.

**Signal model ≠ signal region.** The *model* is the what-if story: what gets made, and what it turns into. The *region* is CMS's net: which catches they keep. That is ε, below.

## The four numbers, one at a time

### 1. σ, the cross section: about 30 pairs per bucket

**σ = 30.1656 ± 2.88 fb.** On average, about **30** golden dolphin pairs are made in every bucket of collisions.

- **Heavier is rarer: the dice game.** Every collision is like rolling two dice, and the pair can only be made if the dice add up to at least its "price" (its weight). Rolling at least 8 happens 15 times in 36; at least 12 happens only once in 36. So a 550 GeV pair is made less often than a 500 GeV one.
- **It's calculated, not measured.** Nobody has ever caught a golden dolphin, so nobody can count them. Theorists work it out from the rules of physics, the way you can work out the dice odds without rolling. They publish a table: the "census book" of the **LHC SUSY Cross Section Working Group**. Go to the row for 550 GeV and read the number.
- **The "±".** The true value is most likely between about 27.3 and 33.0. The rules are known, but some ingredients (how a proton's energy is shared among its quarks) are only known roughly.
- **Watch the currency.** 1 pb = 1,000 fb. Reading 30 fb as 30 pb makes the answer **1,000 times too big** (sub-gap **1a**).

### 2. L, the luminosity: 35.9 buckets

**L = 35.9 fb⁻¹.** CMS swept (recorded) **35.9 buckets** of collisions in 2016. It says nothing about dolphins; it is just how much water was searched. It comes from the paper's abstract on page 1.

- Look-alike units: **fb** (no minus) is σ, *pairs per bucket*. **fb⁻¹** (minus one) is L, *number of buckets*.
- pairs per bucket × buckets = pairs. **30.1656 × 35.9 ≈ 1,083 pairs made in 2016.**

### 3. BR, the branching fraction: 0.101 (about 1 in 10)

BR is **the share of the pairs that ends up with the kind of fish CMS's net is built to catch.**

- The tuna (Z) breaks apart at once in one of three ways: **mud** (quark sprays, called jets) most of the time, **ghosts** (invisible neutrinos) sometimes, or **two silver sardines** (a lepton pair: two electrons, two muons or two taus) only about **1 time in 10**.
- **Why only the tuna.** CMS's net looks for a tuna's fingerprint: two sardines of the same kind, with opposite charges, that together weigh what a tuna weighs (about 91 GeV). A mackerel (W) can never leave that fingerprint. It gives mud, or one sardine plus one ghost, so one of its two pieces is always invisible. The net wants the mackerel's **mud**.
- **Why there's no share for "dolphin → mackerel" or "dolphin → tuna".** In our story those steps **always** happen, 100% of the time. 100% = 1, and multiplying by 1 changes nothing. ("What share of bicycles have two wheels?" All of them.)
- **Bookkeeping choice (convention).** CMS put only the tuna's share into BR. Everything else, including what the mackerel does, is counted by the net's gates, so it sits inside ε. We copy CMS's choice so our numbers line up with their table. Counting a share twice, or forgetting it, is sub-gap **1c**.
- **0.101, not 0.10.** CMS's caption rounds it to 0.10. The particle data book (PDG) gives 3.363% + 3.366% + 3.370% = 0.101, and that's the value CMS's own table uses.
- 1,083 × 0.101 ≈ **109.4 pairs with the right fish** (CMS's table: 109.35 ✓).

### 4. ε, the efficiency: 0.0495 (about 1 in 20)

The net is the **signal region** (the "VZ" region). It is a row of gates, and a catch must pass **every** one. ε is **what's left after the last gate ÷ what came in**.

- The gates, from CMS's *Additional Table 7*: two same-kind sardines that are big enough to see → no third sardine → the sardine pair weighs like a tuna (86–96 GeV) → 2–3 mud clouds → two cleanliness checks (ΔΦ, M_T2) → no b‑type mud → the two mud clouds weigh like a mackerel → **the boat rocked hard (missing energy > 100 GeV)**.
- The biggest loss is at the first gate (109 → 24). Tau sardines don't count, and many sardines are too small or fly where the detector can't see.
- **109.35 in → 5.41 left → ε = 5.41 ÷ 109.35 ≈ 0.0495.**
- **Compartments.** The net sorts catches by how hard the boat rocked. Table 7's rows say "more than X", so subtract neighbouring rows, the way 54 kids taller than 100 cm minus 49 taller than 150 cm leaves 5 between 100 and 150 cm:

| Missing energy (GeV) | 100–150 | 150–250 | 250–350 | > 350 | Total |
| --- | --- | --- | --- | --- | --- |
| Catches | 0.45 | 1.37 | 1.65 | 1.94 | 5.41 |

## The answer

> **30.1656 fb × 35.9 fb⁻¹ × 0.101 × 0.0495 ≈ 5.41 catches**

If 550 GeV golden dolphins existed, CMS's 2016 net would have caught **about 5 extra catches**, mostly in the hard-rocking compartments. CMS saw nothing unusual there, so this kind of dolphin is ruled out.

The four compartment numbers are exactly what the AI must predict in this task, and this ledger is our **answer key** for checking it. Never give it to the test-subject agent.

**Self-check:** σ × L × BR = 109.38 against CMS's 109.35, and the full product is 5.41 against CMS's 5.41. Both match.

## Mistakes made while learning, and the checker test that would catch each

| Slip | What it would do | Sub-gap / check |
| --- | --- | --- |
| Wrote the weight as 500 instead of 550 | σ about 1.5 times too big, from the wrong row | 1d, C4 Match |
| Copied L as 30.5 instead of 35.9 | Count about 15% too small | 1d, wrong input; C2 Source makes it checkable against the page |
| Read fb as pb | Count 1,000 times too big | 1a, C1 Units |
| Used 0.10 instead of 0.101 | Count 1% too small | small, but shows why exact sources matter |
| Counted a share in both BR and ε, or in neither | Count ~10 times too small or too big | 1c, C3 Complete formula |

These are the same slips an AI agent makes. That is the whole point of the checker.
