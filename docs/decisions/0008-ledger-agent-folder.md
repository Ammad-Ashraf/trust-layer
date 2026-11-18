# 0008 — Where the `simple-ledger` agent folder lives

- **Status:** decided
- **Date:** 2026-11-18
- **Decide by:** start of M4 (checker v0)

## Question

Collider-Bench gives the agent our `record-quantity` tool through an agent folder (`agents/<name>/runtime/bin/`), which sits inside the submodule. Where should that folder live?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. Fork Collider-Bench, add one folder, pin the submodule to the fork commit | Additive, pinned, reviewable; upstream code untouched | We maintain a fork; the "CB commit" in manifests becomes the fork commit |
| B. A setup script symlinks `integration/agent/` into the submodule at run time | No fork | Submodule is dirty during runs; the folder's content isn't pinned by the submodule commit |
| C. Derived container image with the CLI installed | No submodule change | Heaviest; changes the image digest; slow to rebuild |

## Claude's lean

A. It is the only option where one commit pins exactly what the agent saw. The fork differs from upstream by one added folder.

## Decision

A, fork Collider-Bench and add one folder. Decided by Claude (Ammad delegated these calls on 2026-11-18): it is the only option where one pinned commit shows exactly what the agent was given.
