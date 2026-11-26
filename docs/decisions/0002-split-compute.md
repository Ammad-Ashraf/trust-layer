# 0002 — Develop small, measure on rented compute

- **Status:** decided; the Study B rental is superseded by [0018](0018-study-b-zero-spend.md) (Study B runs on the runner laptop)
- **Date:** 2026-11-13

## Question

Where do the simulations run? The paper gave each agent 128 CPU cores for 2.5 h.

## Options

| Option | Good | Bad |
| --- | --- | --- |
| FAST / university server | Free | May not have 128 free cores |
| NCP Islamabad (CMS Tier-2) | Right hardware, physics contacts | Slow to arrange, not guaranteed |
| Rent a cloud machine | Ready now, same setup as the paper | Costs money |
| Fewer cores, same 2.5 h limit | Cheap | Runs die by timeout, not by error: a confound |

## Claude's lean

Split compute: develop on small machines, rent 128 vCPU only for the 18 measured runs.

## Decision (Ammad)

Split compute. Development is plain Python on the Windows laptop; dev-phase simulation runs (smoke run, baselines, gate tests) go on the friend's 8-core Linux laptop (correction 2026-11-27: it has 24 cores / 32 threads; full specs in `docs/runner-machine.md`) with tiny N_gen. Study B rents a 128-vCPU EPYC instance for about 20–25 machine-hours (roughly $50–170; verify prices before booking). Fewer cores for Study B is rejected. NCP stays a bonus email, not a dependency.
