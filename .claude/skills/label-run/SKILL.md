---
name: label-run
description: Read one Collider-Bench run (transcript, submitted YAML, evaluator output) and label every mistake with a sub-gap code (1a–1e, 2a–2e, 3a–3f) into the run's labels.yaml. Use when Ammad asks to label, review or read a run or transcript.
---

# Label a run

Input: a run folder `experiments/<exp>/runs/<run-id>/`.

1. Read `manifest.yaml` (task, arm, model) and the task's `tasks/<task>/README.md` and `ledger.yaml`. The ledger is the reference, but never paste it anywhere the test subject can see.
2. Read the transcript (`session.jsonl`, in `raw/` or wherever the manifest points) in full, plus the submitted YAML and the evaluator output.
3. For each mistake, add an entry to `labels.yaml`: `code`, `where` (step or line), `what` (one plain sentence). Codes are defined in `docs/project-summary.md` §3. Gap 1 codes matter most in Phase 1; still record 2x and 3x mistakes when you see them.
4. Mark uncertain labels with `confidence: low` and a note. Don't guess silently.
5. If the checker arm ran, also note each gate bounce: what it flagged, and whether the agent fixed it or argued.

Reply with:

- Counts per code (one line).
- The 1–3 most important mistakes, one line each.
- Anything you weren't sure about.
