# R4 · Prospino LO and NLO cross sections for two Study A tasks — DONE, both sanity checks pass

- **Ran:** `ColliderBench/bin/prospino run --sqrts 13000 --order NLO` (Prospino 2.1, CTEQ6, built in the image on first use) inside `lhc-bench@sha256:8820ecd3…`, `--network=none`, `REPO_ROOT=$CB`, on 2026-11-27 00:31 local. Repo `3361314`, submodule `2986d8b`. No API, no agent, $0.
- **SLHA:** both files start from Prospino's shipped example (`/opt/sim/prospino/prospino.in.les_houches`). The MASS block and the mixing matrices are replaced, and everything not listed is decoupled at 5000 GeV.
  - (a) t̃₁ = 800, χ̃⁰₁ = 400. No stop or sbottom mixing.
  - (b) χ̃±₁ = χ̃⁰₂ = 550, pure wino; χ̃⁰₁ = 200, pure bino. NMIX, U and V are identity, with the higgsinos at 5000.
- **(a) stop pair `tb`, ipart1 = 1:** LO **15.9 fb**, NLO **27.2 fb**, K = 1.71. Run time 16 s (17 s wall, including the first-use build).
- **(b) wino `nn`:**
  - χ̃⁰₂χ̃⁺₁ (ipart 2,5): LO 16.8 fb, NLO 19.8 fb, K = 1.17, 32 s.
  - χ̃⁰₂χ̃⁻₁ (ipart 2,7): LO 6.29 fb, NLO 7.75 fb, K = 1.23, 32 s.
  - **Sum: LO 23.09 fb, NLO 27.55 fb, K = 1.19.**
- **Sanity check vs published NLO+NLL:**
  - (a) 27.2 / 28.33 = 0.960, i.e. **−4.0%**. Pass (within 15%).
  - (b) 27.55 / 30.17 = 0.913, i.e. **−8.7%**. Pass.
  - Both are low, as expected, because NLL resummation is missing. No retries were needed.
- **Odd:**
  - Prospino prints only 3 significant figures (`0.159E-01` pb), so each value is uncertain by about ±0.3%. The JSON reports the `LO_ms/NLO_ms` columns, which differ from `LO/NLO` in the last digit for (b) χ̃⁻.
  - The tool wrote its scratch to `external/collider-bench/prospino_scratch/`, not the working directory. I copied the three `prospino.dat` files out, then deleted that folder, so the submodule is clean.
- **Files:** the 2 SLHA files, the 3 `*.prospino.dat` files and the 3 `*.json` files (the JSON object each run printed, with the `make` build log that preceded it on stdout removed).
