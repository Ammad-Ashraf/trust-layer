# Container integration

How the ledger CLI (`record-quantity`) and the gate get into the Collider-Bench container and onto the agent's PATH, without changing the benchmark image. Written after the smoke run (attachment points 1 and 4).

Mount only `src/trustlayer` (installed) and `integration/subject-claude/`. Never the whole repo.
