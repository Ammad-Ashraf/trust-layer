#!/usr/bin/env python3
"""
CMS-SUS-16-051 compressed signal region analysis.

Applies preselection + compressed selection (Table 3) on Delphes output
and returns binned MET yields normalized to 35.9 fb⁻¹.

Usage: python analysis.py [delphes_chunk0.root delphes_chunk1.root ...]
Default: reads sim/delphes_chunk*.root
"""
import sys
import math
import glob
import uproot
import awkward as ak
import numpy as np
import yaml

# ─── Configuration ─────────────────────────────────────────────────────────
INPUT_FILES  = sys.argv[1:] if len(sys.argv) > 1 else \
    sorted(glob.glob("sim/delphes_chunk*.root"))
OUTPUT_ROOT  = "data/T2tt_800_400_selected.root"
RESULTS_YAML = "results/histogram_T2tt_comp.yaml"

# Normalization
SIGMA_NLO_FB  = 27.2         # Prospino 2.1 NLO, m(stop1)=800 GeV, 13 TeV
LUMINOSITY_FB = 35.9         # CMS 2016

# MET bins from results template [250, 350, 450, 550, inf→capped to 650]
MET_EDGES = [250.0, 350.0, 450.0, 550.0, 650.0]


# ─── Helpers ───────────────────────────────────────────────────────────────
def dphi(phi1, phi2):
    """|Δφ| ∈ [0, π]."""
    d = np.abs(phi1 - phi2)
    return np.where(d > math.pi, 2 * math.pi - d, d)


def ak_firstval(arr, default=0.0):
    """First element per event, or default if empty."""
    has = ak.num(arr) >= 1
    return ak.to_numpy(ak.where(has, ak.firsts(arr, axis=1), default))


def ak_nthval(arr, n, default=999.0):
    """n-th element (0-indexed) per event, or default if fewer than n+1 items."""
    has = ak.num(arr) > n
    padded = ak.pad_none(arr, n + 1, axis=1)
    return ak.to_numpy(ak.where(has, padded[:, n], default))


# ─── Process events ────────────────────────────────────────────────────────
n_total_gen  = 0
n_pass_all   = 0
MET_pass_all = []

for fname in INPUT_FILES:
    print(f"Opening {fname} ...", flush=True)
    tree = uproot.open(f"{fname}:Delphes")

    n_ev = tree.num_entries
    n_total_gen += n_ev

    # ── Load branches ──────────────────────────────────────────────────────
    el_pt  = tree["Electron.PT"].array()
    el_eta = tree["Electron.Eta"].array()
    el_phi = tree["Electron.Phi"].array()
    el_iso = tree["Electron.IsolationVar"].array()

    mu_pt  = tree["Muon.PT"].array()
    mu_eta = tree["Muon.Eta"].array()
    mu_phi = tree["Muon.Phi"].array()
    mu_iso = tree["Muon.IsolationVar"].array()

    jet_pt   = tree["Jet.PT"].array()
    jet_eta  = tree["Jet.Eta"].array()
    jet_phi  = tree["Jet.Phi"].array()
    jet_btag = tree["Jet.BTag"].array()

    met_arr = tree["MissingET.MET"].array()
    phi_arr = tree["MissingET.Phi"].array()
    # Delphes stores exactly one MET object per event
    MET     = ak.to_numpy(ak.flatten(met_arr, axis=None))
    MET_PHI = ak.to_numpy(ak.flatten(phi_arr, axis=None))

    # ── Lepton selection ───────────────────────────────────────────────────
    # Electrons: pT > 20, |η| < 1.442, relative isolation < 0.1
    sel_el = (el_pt > 20) & (np.abs(el_eta) < 1.442) & (el_iso < 0.1)
    # Muons:    pT > 20, |η| < 2.4, relative isolation < 0.1
    sel_mu = (mu_pt > 20) & (np.abs(mu_eta) < 2.4)   & (mu_iso < 0.1)

    n_sel_lep = ak.to_numpy(ak.num(el_pt[sel_el]) + ak.num(mu_pt[sel_mu]))

    # Leading lepton pT and φ (used for MT and compressed Δφ cuts)
    el_lpt  = ak_firstval(el_pt[sel_el])
    el_lphi = ak_firstval(el_phi[sel_el])
    mu_lpt  = ak_firstval(mu_pt[sel_mu])
    mu_lphi = ak_firstval(mu_phi[sel_mu])

    n_el = ak.to_numpy(ak.num(el_pt[sel_el]))
    n_mu = ak.to_numpy(ak.num(mu_pt[sel_mu]))

    lep_pt  = np.where(n_el >= 1, el_lpt,  mu_lpt)
    lep_phi = np.where(n_el >= 1, el_lphi, mu_lphi)

    # ── Jet selection ──────────────────────────────────────────────────────
    # AK4 jets: pT > 30 GeV, |η| < 2.4
    sel_j  = (jet_pt > 30) & (np.abs(jet_eta) < 2.4)
    n_jets = ak.to_numpy(ak.num(jet_pt[sel_j]))

    # ── b-tag ───────────────────────────────────────────────────────────────
    # Delphes BTagging (bit 0): 0 = not b-tagged, 1 = b-tagged (medium WP eff ~65%)
    btag_j  = sel_j & (jet_btag >= 1)
    n_btag  = ak.to_numpy(ak.num(jet_pt[btag_j]))

    # Leading jet b-tag (for compressed: J1 must NOT be b-tagged)
    j1_btag = ak.to_numpy(
        ak.where(
            ak.num(jet_btag[sel_j]) >= 1,
            ak.firsts(jet_btag[sel_j], axis=1),
            ak.zeros_like(ak.num(jet_btag[sel_j]), dtype=float)
        )
    )

    # ── min Δφ(J1,J2, MET) ────────────────────────────────────────────────
    j1_phi  = ak_firstval(jet_phi[sel_j])
    j2_phi  = ak_nthval(jet_phi[sel_j], 1, default=99.0)
    n_j_sel = ak.to_numpy(ak.num(jet_phi[sel_j]))

    dphi_j1_met = dphi(j1_phi, MET_PHI)
    dphi_j2_met = np.where(n_j_sel >= 2, dphi(j2_phi, MET_PHI), math.pi)
    min_dphi    = np.minimum(dphi_j1_met, dphi_j2_met)

    # ── Transverse mass ────────────────────────────────────────────────────
    # MT = sqrt(2 pT(lep) × MET × (1 − cos Δφ))
    dphi_lep_met = dphi(lep_phi, MET_PHI)
    MT = np.sqrt(np.maximum(0, 2 * lep_pt * MET * (1 - np.cos(dphi_lep_met))))

    # ── Δφ(MET, lepton) for compressed cut ───────────────────────────────
    dphi_met_lep = dphi(lep_phi, MET_PHI)

    # ══════════════════════════════════════════════════════════════════════
    # PRESELECTION
    # ══════════════════════════════════════════════════════════════════════
    mask  = MET > 250.0            # MET > 250 GeV
    mask &= n_sel_lep == 1         # exactly one lepton
    mask &= n_jets >= 2            # ≥ 2 jets
    mask &= n_btag >= 1            # ≥ 1 b-tagged jet
    mask &= MT > 150.0             # MT > 150 GeV
    mask &= min_dphi > 0.5         # min Δφ(J1,J2, MET) > 0.5 (compressed: relaxed from 0.8)

    # ══════════════════════════════════════════════════════════════════════
    # COMPRESSED SELECTION (Table 3)
    # ══════════════════════════════════════════════════════════════════════
    mask &= n_jets >= 5             # NJ ≥ 5
    mask &= j1_btag == 0           # J1 not b-tagged (ISR topology)
    mask &= dphi_met_lep < 2.0     # Δφ(MET, lep) < 2 (boost topology)
    mask &= lep_pt < 150.0         # pT(lep) < 150 GeV (soft lepton)

    n_pass = int(np.sum(mask))
    n_pass_all += n_pass
    MET_pass_all.extend(MET[mask].tolist())

    print(f"  {fname}: {n_ev} in, {n_pass} pass ({100.*n_pass/n_ev:.2f}%)", flush=True)

# ─── Histogram ──────────────────────────────────────────────────────────────
print(f"\nTotal: {n_total_gen} generated, {n_pass_all} pass selection", flush=True)

MET_pass = np.array(MET_pass_all)
# Cap overflow into last bin [550, 650)
MET_capped = np.where(MET_pass > 550.0, 599.0, MET_pass)

raw_counts = np.histogram(MET_capped, bins=MET_EDGES)[0]

# ─── Normalize ──────────────────────────────────────────────────────────────
# σ(NLO) × L × (N_pass_bin / N_gen) = expected signal yield
w = SIGMA_NLO_FB * LUMINOSITY_FB / n_total_gen
yields = raw_counts * w

print(f"\nNormalization weight per event: {w:.6f}")
print(f"  σ(NLO) = {SIGMA_NLO_FB} fb")
print(f"  L = {LUMINOSITY_FB} fb⁻¹")
print(f"  N_gen = {n_total_gen}")

print("\nMET bin results:")
for i, (lo, hi) in enumerate(zip(MET_EDGES[:-1], MET_EDGES[1:])):
    label = f"[{int(lo)},{int(hi)})" if hi < 650 else f"[{int(lo)},inf)"
    print(f"  {label}: raw={raw_counts[i]:5d}  yield={yields[i]:.4f}")

print(f"\nTotal yield: {np.sum(yields):.4f} events @ {LUMINOSITY_FB} fb⁻¹")
print(f"Total efficiency: {n_pass_all}/{n_total_gen} = {n_pass_all/n_total_gen:.5f}")

# ─── Save ROOT output ────────────────────────────────────────────────────────
import os; os.makedirs("data", exist_ok=True)
with uproot.recreate(OUTPUT_ROOT) as fout:
    fout["selected"] = {
        "MET":    MET_pass,
    }
    fout["counts"] = {
        "bin_low":    np.array([float(e) for e in MET_EDGES[:-1]]),
        "bin_high":   np.array([float(e) for e in MET_EDGES[1:]]),
        "raw_count":  raw_counts.astype(float),
        "yield":      yields,
    }
print(f"Saved selected events to {OUTPUT_ROOT}", flush=True)

# ─── Write results YAML ──────────────────────────────────────────────────────
# Read template
with open(RESULTS_YAML) as f:
    content = f.read()

parts = content.split("---")
meta_block = parts[0]
hepdata_block = parts[1]

# Parse hepdata block
import re
# Replace null values with computed yields in order
yield_list = [float(f"{y:.6g}") for y in yields]
idx = 0
def replace_null(m):
    global idx
    val = yield_list[idx]
    idx += 1
    return f"{{value: {val}}}"

new_hepdata = re.sub(r"\{value: [^}]+\}", replace_null, hepdata_block)
new_content = meta_block + "---" + new_hepdata

with open(RESULTS_YAML, "w") as f:
    f.write(new_content)
print(f"Updated {RESULTS_YAML}", flush=True)
