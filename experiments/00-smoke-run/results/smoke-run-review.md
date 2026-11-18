# Smoke run review, in plain words (2026-11-18)

This is the first test run: an AI agent did one Collider-Bench task on Israr's laptop, with no checker. The raw record is in `../runs/20261118-0109_sus-16-046_baseline_1/`. This page explains what happened and what it means for us, using everyday analogies.

## The task in one picture: counting fish

The AI must predict **how many signal events** a real experiment (CMS, 2016) would have seen. The formula is:

> expected events = σ × L × BR × ε

Think of it as predicting **how many fish of one species you will catch**:

| Symbol | Physics name | Fishing analogy | Where it comes from |
| --- | --- | --- | --- |
| σ | cross section | how common this fish is in the lake | a calculator called Prospino, or the paper |
| L | luminosity | how much water you swept with your net | fixed: 35.9 fb⁻¹ |
| BR | branching ratio | the share of those fish that are the exact kind you want | physics tables |
| ε | efficiency | how many fish your net actually keeps | the AI's own simulation and cuts |

The first three are **looked up**. The last one, ε, is **built** by the AI: it simulates collisions and then applies filters ("cuts") copied from the paper. ε is the share of events that survive those filters.

## What happened

- **The plumbing works.** The AI ran from start to finish in 28 minutes. At API prices that would cost about $5.68; it ran on the subscription instead.
- **The answer was wrong.** The AI predicted about **1 event**; the right answer is about **55**. The benchmark scores this as a fail. That is normal for this model: the Collider-Bench paper shows it often fails this task.
- **The lookups were right.** σ, L and the units were all correct. The pb → fb step (like grams → kilograms) was done properly.
- **The net had a hole.** The AI's filters kept **1 in 100** events. The right number is about **39 in 100**, so the answer came out about 50× too small.

## Why the net had a hole (my best guess, not yet checked)

- **The event's signature is a photon.** The particle we are looking for decays into a photon, a very bright flash of light.
- **The rule.** One rule from the paper says: *"throw the event away if the photon is right next to a jet"*. A jet is a spray of other particles.
- **The trap.** The detector software also counts the photon's own flash as a jet. So the photon is always "next to a jet", namely itself, and the rule throws away almost every good event.
- **Analogy:** a bouncer told "turn away anyone standing next to a stranger" who mistakes each guest's own shadow for a stranger.
- **To confirm it,** we need the AI's analysis code, which is still on Israr's laptop.

## What this means for our project

**Our checker is like a spell-checker for the formula's arithmetic.** This run's arithmetic was fine. Its mistake was in the net, which is a different kind of error (a "judgment" error, codes 3b/3c). Our checker was never meant to catch that.

**Does this one run cast doubt on our focus? No.**
- It was one short run of one task.
- The Collider-Bench paper measured hundreds of runs. Its tables show that the AI usually gets the shape right but the total wrong.
  - In the analogy, the net is usually fine; the counting is off.
  - That is exactly our Gap 1.
- This run was the unusual case: both the shape and the total were off.
- So it doesn't change the plan. Details: [decision 0014](../../../docs/decisions/0014-drop-failure-mix-runs.md).

**One useful thing did come out of re-reading the tables.** One of our three planned tasks (sus-16-051 T2tt_SRG) is the exception: the AI's mistakes there are in the net, not in the counting. Its sister task T2tt_comp, from the same paper, shows counting mistakes. So it's a better pick for Study B.

## How the checker plugs into the benchmark

**Picture an exam hall.**
- The AI is a student in a sealed room: the container.
- We want to hand it a **notebook** (our ledger tool, `record-quantity`) where it writes down σ, L, BR and ε, each with a unit and a source.
- We also want a **proctor at the door** (the gate, a "Stop hook"). The proctor reads the notebook before the student may hand in, and sends the student back if something is wrong.

**What the test run found:**
- **The proctor works.** We tested it: it can stop the AI, and the AI reads the message and fixes its work. Messages must give full file paths, or the AI looks in the wrong place.
- **The notebook can go in the student's supply drawer.** Collider-Bench gives each kind of student a folder of tools (`agents/<name>/`). We add a copy of the standard student whose drawer also holds our notebook. The normal student is untouched and is our baseline.
- **The room was not clean.** The student's room got a copy of Ammad's personal Claude settings, including email and Drive connectors. Israr switched them off by hand for this run, but that has to be fixed for good (decision 0010).
- **One open risk.** The student has full rights inside its room, so in theory it could tear the proctor's instructions off the door. We will log every proctor visit outside the room and check the instructions after each run.

## Decisions made (Ammad delegated these to Claude on 2026-11-18)

| # | Question | Choice | Why, in one line |
| --- | --- | --- | --- |
| [0008](../../../docs/decisions/0008-ledger-agent-folder.md) | Where does our tool folder live? | Our own copy (fork) of Collider-Bench, plus one added folder | One saved snapshot shows exactly what the AI was given |
| [0009](../../../docs/decisions/0009-pint-in-container.md) | The unit library `pint` is missing in the container | Drop it there; use a small fixed unit table | We only need four units: a ruler, not a whole lab |
| [0010](../../../docs/decisions/0010-subject-isolation.md) | How do we keep the AI's room clean? | A separate user account on Israr's laptop just for the test AI | Clean by design, so nobody has to remember to tidy up |
| [0011](../../../docs/decisions/0011-auth-for-measured-runs.md) | Subscription or API key? | Subscription for practice runs, API key for Study B | Practice is free; Study B needs long runs that don't stop |
| [0012](../../../docs/decisions/0012-commit-transcripts.md) | Save the AI's transcripts in the repo? | Yes, compressed (about 0.3 MB each) | They are the evidence behind every mistake we label |
| [0014](../../../docs/decisions/0014-drop-failure-mix-runs.md) | Count mistake types before Study B? | No (replaces 0013) | The paper's tables already answer it; one run can't outweigh hundreds |

Still with Ammad, because they set how much money we spend:
- 0005 (which model);
- 0006 (budget);
- 0007 (Haiku arm).

They can be decided now, using the paper's tables.

## Small fixes still to do

- Use the full task id (`sus-16-046_sim-T5Wg`) in run manifests.
- Rename the `tasks/` folders to match the full task ids.
