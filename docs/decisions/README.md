# Decisions

One file per decision, numbered in order: `NNNN-short-name.md`. Copy [`0000-template.md`](0000-template.md).

Claude gives the options and a lean; Ammad decides and writes one line on why. Status is `open`, `decided` or `superseded by NNNN`. Never rewrite a decided record: supersede it with a new one.

| # | Decision | Status |
| --- | --- | --- |
| [0001](0001-gate-over-advisory-tool.md) | The checker reaches the agent as a gate, not an advisory tool | decided |
| [0002](0002-split-compute.md) | Develop small, measure on rented compute | decided |
| [0003](0003-two-machines-one-repo.md) | Two machines, one repo | decided |
| [0004](0004-repo-layout.md) | Repo layout, Collider-Bench as a submodule, papers not committed | decided |
| [0005](0005-study-b-model.md) | Which model Study B tests | decided |
| [0006](0006-budget-cap.md) | Budget cap | superseded by 0018 |
| [0007](0007-haiku-arm.md) | Add a Haiku 4.5 arm | decided |
| [0008](0008-ledger-agent-folder.md) | Where the `simple-ledger` agent folder lives | decided |
| [0009](0009-pint-in-container.md) | `pint` inside the container | decided |
| [0010](0010-subject-isolation.md) | Isolating the test-subject agent's settings | decided |
| [0011](0011-auth-for-measured-runs.md) | Auth for measured runs | decided |
| [0012](0012-commit-transcripts.md) | Commit run transcripts? | decided |
| [0013](0013-baseline-failure-mix.md) | Check the baseline failure mix before fixing Study B tasks | superseded by 0014 |
| [0014](0014-drop-failure-mix-runs.md) | Drop the extra failure-mix runs; choose Study B tasks from the paper's tables | decided |
| [0015](0015-frontend-plain-html.md) | Frontend: plain HTML, CSS and JavaScript | decided |
| [0016](0016-study-a-preregistration.md) | Fix Study A's injections and tolerance before building the checks | decided |
| [0017](0017-verify-sigma-provenance.md) | Should C2 verify where sigma came from, not just its label? | decided |
| [0018](0018-study-b-zero-spend.md) | Study B spends nothing: Israr's Max subscription, on the runner laptop | decided |
| [0019](0019-study-b-walltime.md) | Study B time limit: 10 h, a pilot, fixed timeout reporting | decided |
