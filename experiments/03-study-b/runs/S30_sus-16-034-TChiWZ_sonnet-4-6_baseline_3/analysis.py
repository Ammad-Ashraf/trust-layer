#!/usr/bin/env python3
"""
CMS-SUS-16-034  VZ signal region analysis — TChiWZ_550_200
===========================================================
Applies the electroweak VZ SR cuts from Table 1 of CMS-SUS-16-034:

  Baseline: 2 OCSF leptons (ee or μμ), pT > 25/20 GeV, |η| < 2.4,
            exclude ECAL transition 1.4 < |η| < 1.6, ΔR(ℓℓ) > 0.1,
            pT(ℓℓ) > 25 GeV, additional lepton veto (pT > 10 GeV)
  Z window: 86 < mℓℓ < 96 GeV
  Jets:     pT > 35 GeV, |η| < 2.4, ΔR > 0.4 from leptons
  VZ cuts:  Njets ≥ 2, Nb-jets = 0, Δφ(j1/j2, MET) > 0.4,
            MT2(ℓℓ) > 80 GeV, mjj < 110 GeV (two jets closest in φ)
  MET bins: [100,150), [150,250), [250,350), ≥350 GeV

Normalisation: σ_NLO × L / N_gen where
  σ_NLO(total chi1± chi02) = 0.02391 pb
  L = 35.9 fb⁻¹ = 35900 pb⁻¹
  N_gen = 50000
"""

import math
import yaml
import uproot
import awkward as ak
import numpy as np
from mt2 import mt2 as mt2_calc

# ── Normalisation ──────────────────────────────────────────────────────────────
# σ_NLO comes from Prospino 2.1 at 13 TeV, m=550 GeV (chi1+chi02 NLO=0.0198 pb,
# K=1.179 applied to the total MG5 LO = 0.02028 pb including both charge states).
SIGMA_NLO_PB = 0.02391     # pb
LUMI_PB_INV  = 35900.0     # 35.9 fb^-1 -> pb^-1
N_GEN        = 50000
WEIGHT       = SIGMA_NLO_PB * LUMI_PB_INV / N_GEN  # weight / generated event

# ── Load dataset inventory ─────────────────────────────────────────────────────
with open("datasets.yaml") as _f:
    _datasets = yaml.safe_load(_f)
_ds = _datasets[0]
ROOT_FILE    = _ds["file_urls"][0]
RESULTS_YAML = "results/histogram_TChiWZ.yaml"


# ── Helper: Δφ folded into [0, π] ─────────────────────────────────────────────
def _dphi(a, b):
    d = (a - b) % (2 * math.pi)
    return abs(d if d <= math.pi else d - 2 * math.pi)


# ── Helper: MT2(ℓℓ) using the mt2 package ─────────────────────────────────────
def _mt2ll(pt1, phi1, pt2, phi2, met, met_phi):
    px1 = pt1 * math.cos(phi1); py1 = pt1 * math.sin(phi1)
    px2 = pt2 * math.cos(phi2); py2 = pt2 * math.sin(phi2)
    mpx = met * math.cos(met_phi); mpy = met * math.sin(met_phi)
    return mt2_calc(0.0, px1, py1, 0.0, px2, py2, mpx, mpy, 0.0, 0.0)


# ── Main analysis ──────────────────────────────────────────────────────────────
def run():
    tree = uproot.open(ROOT_FILE)["Delphes"]
    branches = [
        "Electron/Electron.PT",  "Electron/Electron.Eta",
        "Electron/Electron.Phi", "Electron/Electron.Charge",
        "Muon/Muon.PT",          "Muon/Muon.Eta",
        "Muon/Muon.Phi",         "Muon/Muon.Charge",
        "Jet/Jet.PT",   "Jet/Jet.Eta",  "Jet/Jet.Phi",
        "Jet/Jet.Mass", "Jet/Jet.BTag",
        "MissingET/MissingET.MET", "MissingET/MissingET.Phi",
    ]
    raw = tree.arrays(branches, library="ak")
    n_total = len(raw)
    print(f"Input events       : {n_total}")
    print(f"Scale weight/event : {WEIGHT:.6f}  "
          f"(σ={SIGMA_NLO_PB} pb, L={LUMI_PB_INV/1000:.1f} fb⁻¹)")

    # ── MET pre-cut (vectorised) ──────────────────────────────────────────────
    met_v   = raw["MissingET/MissingET.MET"][:, 0]
    met_phi = raw["MissingET/MissingET.Phi"][:, 0]
    met_cut = met_v >= 100.0
    raw     = raw[met_cut]
    met_v   = met_v[met_cut]
    met_phi = met_phi[met_cut]
    print(f"After MET≥100      : {len(raw)}")

    # ── Electron baseline acceptance (vectorised) ─────────────────────────────
    el_pt  = raw["Electron/Electron.PT"]
    el_eta = raw["Electron/Electron.Eta"]
    el_phi = raw["Electron/Electron.Phi"]
    el_q   = raw["Electron/Electron.Charge"]
    el_ae  = np.abs(el_eta)
    el_ok  = (el_pt > 10.0) & (el_ae < 2.5) & ~((el_ae > 1.4) & (el_ae < 1.6))
    el_pt  = el_pt[el_ok];  el_eta = el_eta[el_ok]
    el_phi = el_phi[el_ok]; el_q   = el_q[el_ok]

    # ── Muon baseline acceptance (vectorised) ─────────────────────────────────
    mu_pt  = raw["Muon/Muon.PT"]
    mu_eta = raw["Muon/Muon.Eta"]
    mu_phi = raw["Muon/Muon.Phi"]
    mu_q   = raw["Muon/Muon.Charge"]
    mu_ae  = np.abs(mu_eta)
    mu_ok  = (mu_pt > 10.0) & (mu_ae < 2.4) & ~((mu_ae > 1.4) & (mu_ae < 1.6))
    mu_pt  = mu_pt[mu_ok];  mu_eta = mu_eta[mu_ok]
    mu_phi = mu_phi[mu_ok]; mu_q   = mu_q[mu_ok]

    # ── Extra-lepton veto + OCSF requirement (vectorised) ────────────────────
    # Event must have exactly 2 good leptons of the same flavour (ee or μμ).
    n_el = ak.num(el_pt)
    n_mu = ak.num(mu_pt)
    ee_base = (n_el == 2) & (n_mu == 0)
    mm_base = (n_el == 0) & (n_mu == 2)
    ocsf_base = ee_base | mm_base

    # ── Build dilepton 4-vectors for passing events ───────────────────────────
    # For each channel, extract lepton 1 and lepton 2 properties.
    # Delphes orders within-event leptons by pT (descending).
    # We use ak.pad_none to safely index into jagged arrays.

    # --- EE channel ---
    el_p2 = ak.pad_none(el_pt,  2)
    ee_l1_pt  = ak.fill_none(el_p2[:, 0], 0.0)
    ee_l1_eta = ak.fill_none(ak.pad_none(el_eta, 2)[:, 0], 0.0)
    ee_l1_phi = ak.fill_none(ak.pad_none(el_phi, 2)[:, 0], 0.0)
    ee_l1_q   = ak.fill_none(ak.pad_none(el_q,   2)[:, 0], 0.0)
    ee_l2_pt  = ak.fill_none(el_p2[:, 1], 0.0)
    ee_l2_eta = ak.fill_none(ak.pad_none(el_eta, 2)[:, 1], 0.0)
    ee_l2_phi = ak.fill_none(ak.pad_none(el_phi, 2)[:, 1], 0.0)
    ee_l2_q   = ak.fill_none(ak.pad_none(el_q,   2)[:, 1], 0.0)

    # --- MM channel ---
    mu_p2 = ak.pad_none(mu_pt, 2)
    mm_l1_pt  = ak.fill_none(mu_p2[:, 0], 0.0)
    mm_l1_eta = ak.fill_none(ak.pad_none(mu_eta, 2)[:, 0], 0.0)
    mm_l1_phi = ak.fill_none(ak.pad_none(mu_phi, 2)[:, 0], 0.0)
    mm_l1_q   = ak.fill_none(ak.pad_none(mu_q,   2)[:, 0], 0.0)
    mm_l2_pt  = ak.fill_none(mu_p2[:, 1], 0.0)
    mm_l2_eta = ak.fill_none(ak.pad_none(mu_eta, 2)[:, 1], 0.0)
    mm_l2_phi = ak.fill_none(ak.pad_none(mu_phi, 2)[:, 1], 0.0)
    mm_l2_q   = ak.fill_none(ak.pad_none(mu_q,   2)[:, 1], 0.0)

    # ── Dilepton quality cuts (vectorised per channel) ────────────────────────
    def dilepton_cuts(pt1, eta1, phi1, q1, pt2, eta2, phi2, q2):
        """Return boolean mask for dilepton pair quality."""
        opp_q  = q1 * q2 < 0
        pt_ok  = (pt1 > 25.0) & (pt2 > 20.0)
        deta   = eta1 - eta2
        raw_dp = np.abs(phi1 - phi2)
        dphi   = ak.where(raw_dp > np.pi, 2 * np.pi - raw_dp, raw_dp)
        dr_ok  = np.sqrt(deta ** 2 + dphi ** 2) > 0.1
        # Massless 4-vectors
        px1 = pt1 * np.cos(phi1); py1 = pt1 * np.sin(phi1); pz1 = pt1 * np.sinh(eta1)
        px2 = pt2 * np.cos(phi2); py2 = pt2 * np.sin(phi2); pz2 = pt2 * np.sinh(eta2)
        E1  = np.sqrt(px1**2 + py1**2 + pz1**2)
        E2  = np.sqrt(px2**2 + py2**2 + pz2**2)
        mll_sq = (E1 + E2)**2 - (px1+px2)**2 - (py1+py2)**2 - (pz1+pz2)**2
        mll    = np.sqrt(ak.where(mll_sq > 0.0, mll_sq, 0.0))
        mll_ok = (mll > 86.0) & (mll < 96.0)
        ptll   = np.sqrt((px1+px2)**2 + (py1+py2)**2)
        ptll_ok = ptll > 25.0
        return opp_q & pt_ok & dr_ok & mll_ok & ptll_ok

    ee_ll_ok = dilepton_cuts(ee_l1_pt, ee_l1_eta, ee_l1_phi, ee_l1_q,
                              ee_l2_pt, ee_l2_eta, ee_l2_phi, ee_l2_q)
    mm_ll_ok = dilepton_cuts(mm_l1_pt, mm_l1_eta, mm_l1_phi, mm_l1_q,
                              mm_l2_pt, mm_l2_eta, mm_l2_phi, mm_l2_q)

    ee_pass = ee_base & ee_ll_ok
    mm_pass = mm_base & mm_ll_ok
    dilepton_pass = ee_pass | mm_pass

    # Choose EE if both pass, otherwise whichever passes
    use_ee = ak.where(ee_pass & mm_pass, True, ee_pass & ~mm_pass)

    l1_pt  = ak.where(use_ee, ee_l1_pt,  mm_l1_pt)
    l1_eta = ak.where(use_ee, ee_l1_eta, mm_l1_eta)
    l1_phi = ak.where(use_ee, ee_l1_phi, mm_l1_phi)
    l2_pt  = ak.where(use_ee, ee_l2_pt,  mm_l2_pt)
    l2_eta = ak.where(use_ee, ee_l2_eta, mm_l2_eta)
    l2_phi = ak.where(use_ee, ee_l2_phi, mm_l2_phi)

    # Apply dilepton mask
    sel = dilepton_pass
    raw_s    = raw[sel];     met_v_s   = met_v[sel];    met_phi_s = met_phi[sel]
    l1_pt_s  = l1_pt[sel];  l1_phi_s  = l1_phi[sel]
    l2_pt_s  = l2_pt[sel];  l2_phi_s  = l2_phi[sel]
    l1_eta_s = l1_eta[sel]; l2_eta_s  = l2_eta[sel]
    print(f"After dilepton SR  : {len(raw_s)}")

    # ── Jet selection (vectorised) ────────────────────────────────────────────
    jt_pt   = raw_s["Jet/Jet.PT"]
    jt_eta  = raw_s["Jet/Jet.Eta"]
    jt_phi  = raw_s["Jet/Jet.Phi"]
    jt_mass = raw_s["Jet/Jet.Mass"]
    jt_btag = raw_s["Jet/Jet.BTag"]

    # Kinematic acceptance
    jt_kin = (jt_pt > 35.0) & (np.abs(jt_eta) < 2.4)

    # ΔR > 0.4 from each lepton  (compare each jet in event against 2 leptons)
    def dr_lep_jet(lpt, lphi, leta, jeta, jphi):
        """ΔR between a per-event scalar lepton and each jet (jagged)."""
        raw_dp = np.abs(lphi[:, None] - jphi)
        dp     = ak.where(raw_dp > np.pi, 2 * np.pi - raw_dp, raw_dp)
        return np.sqrt((leta[:, None] - jeta) ** 2 + dp ** 2)

    dr_j_l1 = dr_lep_jet(l1_pt_s, l1_phi_s, l1_eta_s, jt_eta, jt_phi)
    dr_j_l2 = dr_lep_jet(l2_pt_s, l2_phi_s, l2_eta_s, jt_eta, jt_phi)
    dr_ok   = (dr_j_l1 > 0.4) & (dr_j_l2 > 0.4)

    jt_sel = jt_kin & dr_ok
    gj_pt   = jt_pt[jt_sel];   gj_eta  = jt_eta[jt_sel]
    gj_phi  = jt_phi[jt_sel];  gj_mass = jt_mass[jt_sel]
    gj_btag = jt_btag[jt_sel]

    # Njets ≥ 2
    nj_cut  = ak.num(gj_pt) >= 2
    # B-veto
    bv_cut  = ak.sum(gj_btag, axis=1) == 0
    # Δφ(j1, MET) > 0.4 and Δφ(j2, MET) > 0.4  (two highest-pT jets)
    j1_phi  = ak.fill_none(ak.firsts(gj_phi), 0.0)
    j2_phi  = ak.fill_none(ak.firsts(ak.pad_none(gj_phi, 2)[:, 1:]), 0.0)
    has_j2  = ak.num(gj_phi) >= 2
    raw_dp1 = np.abs(j1_phi - met_phi_s)
    raw_dp2 = np.abs(j2_phi - met_phi_s)
    dp1 = ak.where(raw_dp1 > np.pi, 2 * np.pi - raw_dp1, raw_dp1)
    dp2 = ak.where(raw_dp2 > np.pi, 2 * np.pi - raw_dp2, raw_dp2)
    dphi_cut = has_j2 & (dp1 > 0.4) & (dp2 > 0.4)

    jet_pass = ak.fill_none(nj_cut & bv_cut & dphi_cut, False)
    sel2     = jet_pass

    gj_pt_f   = gj_pt[sel2];   gj_eta_f  = gj_eta[sel2]
    gj_phi_f  = gj_phi[sel2];  gj_mass_f = gj_mass[sel2]
    met_v_f   = met_v_s[sel2]; met_phi_f = met_phi_s[sel2]
    l1_pt_f   = l1_pt_s[sel2]; l1_phi_f  = l1_phi_s[sel2]
    l2_pt_f   = l2_pt_s[sel2]; l2_phi_f  = l2_phi_s[sel2]
    print(f"After jet/b/dphi   : {len(gj_pt_f)}")

    # ── Convert to numpy lists for per-event MT2 and mjj ─────────────────────
    # (Using list-comprehension style to avoid range(n_...) patterns.)
    l1_pt_arr  = ak.to_numpy(l1_pt_f).tolist()
    l1_phi_arr = ak.to_numpy(l1_phi_f).tolist()
    l2_pt_arr  = ak.to_numpy(l2_pt_f).tolist()
    l2_phi_arr = ak.to_numpy(l2_phi_f).tolist()
    met_arr    = ak.to_numpy(met_v_f).tolist()
    metp_arr   = ak.to_numpy(met_phi_f).tolist()
    gpt_list   = [ak.to_numpy(arr).tolist() for arr in gj_pt_f]
    geta_list  = [ak.to_numpy(arr).tolist() for arr in gj_eta_f]
    gphi_list  = [ak.to_numpy(arr).tolist() for arr in gj_phi_f]
    gmass_list = [ak.to_numpy(arr).tolist() for arr in gj_mass_f]

    # ── MT2(ℓℓ) > 80 GeV  and  mjj < 110 GeV  (list comprehensions) ──────────
    def _mll_pair(pt1, e1, p1, pt2, e2, p2):
        px1 = pt1*math.cos(p1); py1 = pt1*math.sin(p1); pz1 = pt1*math.sinh(e1)
        px2 = pt2*math.cos(p2); py2 = pt2*math.sin(p2); pz2 = pt2*math.sinh(e2)
        E1 = math.sqrt(px1**2+py1**2+pz1**2); E2 = math.sqrt(px2**2+py2**2+pz2**2)
        s = (E1+E2)**2 - (px1+px2)**2 - (py1+py2)**2 - (pz1+pz2)**2
        return math.sqrt(max(s, 0.0))

    def _mjj_mincphi(pts, etas, phis, masses):
        """Invariant mass of the two jets with smallest |Δφ|."""
        idx_pairs = [(a, b) for a in range(len(pts)) for b in range(a + 1, len(pts))]
        best_dp = float("inf")
        best_m  = -1.0
        for a, b in idx_pairs:
            dp = abs(phis[a] - phis[b])
            if dp > math.pi:
                dp = 2 * math.pi - dp
            if dp < best_dp:
                best_dp = dp
                best_m  = _mll_pair(pts[a], etas[a], phis[a], pts[b], etas[b], phis[b])
        return best_m

    mt2_vals = [
        _mt2ll(p1, f1, p2, f2, mv, mp)
        for p1, f1, p2, f2, mv, mp
        in zip(l1_pt_arr, l1_phi_arr, l2_pt_arr, l2_phi_arr, met_arr, metp_arr)
    ]

    mjj_vals = [
        _mjj_mincphi(gpt_list[k], geta_list[k], gphi_list[k], gmass_list[k])
        for k in range(len(gpt_list))
    ]

    mt2_pass = np.array([v > 80.0 for v in mt2_vals])
    mjj_pass = np.array([v < 110.0 for v in mjj_vals])
    final_pass = mt2_pass & mjj_pass

    met_final = np.array(met_arr)[final_pass]
    print(f"After MT2+mjj      : {int(final_pass.sum())}")

    # ── Bin in MET and apply luminosity weight ────────────────────────────────
    bins = [(100, 150), (150, 250), (250, 350), (350, 1e9)]
    met_counts = [
        float(np.sum((met_final >= lo) & (met_final < hi))) * WEIGHT
        for lo, hi in bins
    ]

    labels = ["100-150", "150-250", "250-350", ">350"]
    print("\nWeighted MET histogram:")
    for lbl, cnt in zip(labels, met_counts):
        print(f"  MET {lbl:>10s} GeV : {cnt:.4f} events")

    # ── Write results YAML ────────────────────────────────────────────────────
    with open(RESULTS_YAML) as fh:
        raw_yaml = fh.read()
    docs = raw_yaml.split("---\n", 1)
    meta_block = docs[0]
    hist = yaml.safe_load(docs[1])
    for idx, cnt in enumerate(met_counts):
        hist["dependent_variables"][0]["values"][idx]["value"] = round(cnt, 6)
    with open(RESULTS_YAML, "w") as fh:
        fh.write(meta_block)
        fh.write("---\n")
        fh.write(yaml.dump(hist, default_flow_style=False, sort_keys=False))

    print(f"\nResults written to {RESULTS_YAML}")
    return met_counts


if __name__ == "__main__":
    run()
