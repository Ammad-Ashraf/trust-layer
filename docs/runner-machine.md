# Runner machine (Israr's laptop)

Specs as reported by the runner session on 2026-11-27. Every run manifest pins the machine by the short name `runner-laptop-24c` and the `nproc` value, and this page holds the rest.

| Part | Value |
| --- | --- |
| Machine | HP OMEN 16 (16-wf0xxx), firmware F.26, hostname `deneb-OMEN` |
| OS | Ubuntu 26.04.1 LTS, Linux 7.0.0-44-generic, x86-64 |
| CPU | Intel Core i9-13900HX: 24 cores / 32 threads, up to 5.4 GHz; L2 32 MiB, L3 36 MiB |
| RAM | 30 GiB, plus 8 GiB swap |
| Disk | 1 TB NVMe SSD (KIOXIA KBG50ZNV1T02), 778 GB free on `/` |
| GPU | NVIDIA GeForce RTX 4060 Laptop, 8 GB (driver 595.99.02), plus Intel UHD. Not used by the benchmark |
| Software | Podman 5.7.0 (rootless), Python 3.14.4 (host), Claude Code 2.1.326, git 2.53.0 |
| Benchmark image | `ghcr.io/dfaroughy/lhc-bench@sha256:8820ecd3b8cada3d37e5e16214bedc53b07cbc58ea83ef104f1795e3f9b3c01f` (Python 3.11.15 inside) |

## What it means for the studies

- **Development runs** (smoke run, gate tests, Prospino, cheap checker-arm runs): this machine is enough.
- **Study B:** runs here too ([0018](decisions/0018-study-b-zero-spend.md)), one run at a time, as user `tlsubject`, on Israr's Max subscription. The paper gave each agent 128 cores for 2.5 hours; this laptop has 32 threads. To keep the same total compute, the limit is 10 h instead of 2.5 h ([0019](decisions/0019-study-b-walltime.md)), there's a 3-run pilot first, and timeouts are reported per arm and never rerun.
