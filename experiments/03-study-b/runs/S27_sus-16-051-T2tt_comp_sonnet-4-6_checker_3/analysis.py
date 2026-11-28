"""
CMS-SUS-16-051 Compressed Signal Region Analysis
Signal: T2tt_800_400 (stop 800 GeV, neutralino 400 GeV)
Reference: Table 3 (compressed selection) + Table 1 (preselection)

Selection requirements:
  Preselection (Table 1):
    - Exactly 1 e (pT>20, |eta|<1.442) or mu (pT>20, |eta|<2.4)
    - MET > 250 GeV
    - min dphi(J1,J2, MET) > 0.5 (relaxed from 0.8 for compressed)
    - MT > 150 GeV
    - Veto on 2nd lepton
    - >= 2 jets (pT>30, |eta|<2.4), >= 1 b-tagged jet (medium WP)

  Compressed (Table 3):
    - NJ >= 5
    - J1 (leading jet) NOT b-tagged (medium WP CSVv2)
    - dphi(MET, lepton) < 2
    - min dphi(J1,J2, MET) > 0.5
    - pT(lepton) < 150 GeV

  MET bins: [250,350), [350,450), [450,550), [550, inf)
"""

import numpy as np
import awkward as ak
import uproot
import yaml
from pathlib import Path

# ── Load configuration from datasets.yaml ────────────────────────────────────
WORKSPACE = Path(__file__).parent
with open(WORKSPACE / "datasets.yaml") as _f:
    _datasets = yaml.safe_load(_f)

_ds = _datasets[0]
INPUT_ROOT = WORKSPACE / _ds["file_urls"][0]
N_GEN      = _ds["events"]
SIGMA_NLO_PB = _ds["cross_section_pb"]

LUMI_FB = 35.9    # CMS 2016 dataset, CMS-SUS-16-051
RESULTS_YAML = WORKSPACE / "results" / "histogram_T2tt_comp.yaml"

# Event weight: (sigma_NLO [fb]) * L [fb^-1] / N_gen
EVENT_WEIGHT = (SIGMA_NLO_PB * 1000.0) * LUMI_FB / N_GEN


def dphi(phi1, phi2):
    """Compute |Δφ| ∈ [0, π]."""
    d = np.abs(phi1 - phi2)
    return np.where(d > np.pi, 2 * np.pi - d, d)


def compute_mt(lep_pt, lep_phi, met, met_phi):
    """Transverse mass MT = sqrt(2 * pT_lep * MET * (1 - cos(Δφ(lep, MET))))."""
    dp = dphi(lep_phi, met_phi)
    return np.sqrt(2.0 * lep_pt * met * (1.0 - np.cos(dp)))


def run_analysis():
    print(f"Opening {INPUT_ROOT}")
    print(f"Event weight (σ·L/N_gen): {EVENT_WEIGHT:.6f}")
    print(f"Expected if 100% sel eff: {SIGMA_NLO_PB * 1000.0 * LUMI_FB:.2f}")

    f = uproot.open(str(INPUT_ROOT))
    tree = f["Delphes"]
    n_total = tree.num_entries
    print(f"Total events: {n_total}")

    # ── Load branches ────────────────────────────────────────────────────────
    el_pt  = tree["Electron/Electron.PT"].array()
    el_eta = tree["Electron/Electron.Eta"].array()
    el_phi = tree["Electron/Electron.Phi"].array()

    mu_pt  = tree["Muon/Muon.PT"].array()
    mu_eta = tree["Muon/Muon.Eta"].array()
    mu_phi = tree["Muon/Muon.Phi"].array()

    jet_pt   = tree["Jet/Jet.PT"].array()
    jet_eta  = tree["Jet/Jet.Eta"].array()
    jet_phi  = tree["Jet/Jet.Phi"].array()
    jet_btag = tree["Jet/Jet.BTag"].array()

    met_arr     = ak.flatten(tree["MissingET/MissingET.MET"].array(), axis=1).to_numpy()
    met_phi_arr = ak.flatten(tree["MissingET/MissingET.Phi"].array(), axis=1).to_numpy()

    n_ev = n_total

    # ── Lepton selection ─────────────────────────────────────────────────────
    # Electrons: pT > 20 GeV, |η| < 1.442
    sel_el = (el_pt > 20.0) & (np.abs(el_eta) < 1.442)
    # Muons: pT > 20 GeV, |η| < 2.4
    sel_mu = (mu_pt > 20.0) & (np.abs(mu_eta) < 2.4)

    n_sel_el = ak.sum(sel_el, axis=1).to_numpy()
    n_sel_mu = ak.sum(sel_mu, axis=1).to_numpy()
    n_lep = n_sel_el + n_sel_mu

    has_exactly_1_lep = (n_lep == 1)
    has_el = (n_sel_el == 1) & (n_sel_mu == 0)
    has_mu = (n_sel_mu == 1) & (n_sel_el == 0)

    # First selected lepton
    el_first_pt  = ak.fill_none(ak.firsts(el_pt[sel_el],  axis=1), 0.0).to_numpy()
    el_first_phi = ak.fill_none(ak.firsts(el_phi[sel_el], axis=1), 0.0).to_numpy()
    mu_first_pt  = ak.fill_none(ak.firsts(mu_pt[sel_mu],  axis=1), 0.0).to_numpy()
    mu_first_phi = ak.fill_none(ak.firsts(mu_phi[sel_mu], axis=1), 0.0).to_numpy()

    lep_pt_arr  = np.where(has_el, el_first_pt,  mu_first_pt)
    lep_phi_arr = np.where(has_el, el_first_phi, mu_first_phi)

    # ── Jet selection ─────────────────────────────────────────────────────────
    # Jets: pT > 30 GeV, |η| < 2.4
    sel_jet = (jet_pt > 30.0) & (np.abs(jet_eta) < 2.4)

    sel_jets_phi  = jet_phi[sel_jet]
    sel_jets_btag = jet_btag[sel_jet]

    n_sel_jet = ak.sum(sel_jet, axis=1).to_numpy()

    # b-tagging: Delphes CMS card uses a single BTagging module with BitNumber=0
    # (see delphes_card_CMS.tcl), so BTag=1 means b-tagged at the parametrized WP
    # (efficiency ~60-70% for pT 30-400 GeV, matching CMS medium WP CSVv2)
    btag_medium = (sel_jets_btag & 1) > 0
    n_btag_medium = ak.sum(btag_medium, axis=1).to_numpy()

    # ── Angular variables ─────────────────────────────────────────────────────
    met     = met_arr
    met_phi = met_phi_arr

    # min Δφ(J1, J2, MET)
    j1_phi = ak.fill_none(ak.firsts(sel_jets_phi, axis=1), 0.0).to_numpy()
    j2_phi = ak.fill_none(ak.firsts(sel_jets_phi[:, 1:], axis=1), 0.0).to_numpy()
    has_2j = n_sel_jet >= 2

    dphi_j1_met = dphi(j1_phi, met_phi)
    dphi_j2_met = dphi(j2_phi, met_phi)
    min_dphi_j12_met = np.where(has_2j, np.minimum(dphi_j1_met, dphi_j2_met), 0.0)

    # Δφ(MET, lepton)
    dphi_met_lep = dphi(met_phi, lep_phi_arr)

    # Transverse mass
    mt = compute_mt(lep_pt_arr, lep_phi_arr, met, met_phi)

    # Is leading jet b-tagged (medium WP)?
    j1_btag = ak.fill_none(ak.firsts(btag_medium, axis=1), False).to_numpy().astype(bool)

    # ── Preselection ──────────────────────────────────────────────────────────
    presel = (
        has_exactly_1_lep      &   # exactly 1 lepton
        (met > 250.0)          &   # MET > 250 GeV
        (mt  > 150.0)          &   # MT  > 150 GeV
        (min_dphi_j12_met > 0.5) & # min Δφ(J1,2, MET) > 0.5 (compressed relaxes 0.8)
        (n_sel_jet >= 2)       &   # >= 2 selected jets
        (n_btag_medium >= 1)       # >= 1 b-tagged jet (medium WP)
    )

    # ── Compressed selection (Table 3) ────────────────────────────────────────
    compressed = (
        presel                 &
        (n_sel_jet >= 5)       &   # NJ >= 5
        (~j1_btag)             &   # J1 not b-tagged (ISR jet)
        (dphi_met_lep < 2.0)   &   # Δφ(MET, lepton) < 2
        (lep_pt_arr < 150.0)       # lepton pT < 150 GeV
    )

    print(f"\n--- Selection yields ---")
    print(f"After preselection:  {np.sum(presel):6d} events")
    print(f"After compressed:    {np.sum(compressed):6d} events")

    # ── MET histogram ─────────────────────────────────────────────────────────
    met_pass = met[compressed]

    counts = np.array([
        np.sum((met_pass >= 250.) & (met_pass < 350.)),
        np.sum((met_pass >= 350.) & (met_pass < 450.)),
        np.sum((met_pass >= 450.) & (met_pass < 550.)),
        np.sum(met_pass >= 550.),
    ])

    yields = counts * EVENT_WEIGHT

    print(f"\n--- MET histogram ---")
    for lo, hi, c, y in zip([250,350,450,550],[350,450,550,'inf'], counts, yields):
        print(f"  [{lo}, {hi}): {c:.0f} raw → {y:.4f} expected")
    print(f"  Total expected: {np.sum(yields):.4f}")

    eff = np.sum(compressed) / N_GEN
    print(f"  Selection efficiency ε = {np.sum(compressed)}/{N_GEN} = {eff:.6f}")

    return yields, counts


def update_yaml(yields):
    with open(str(RESULTS_YAML)) as f:
        content = f.read()

    docs = list(yaml.safe_load_all(content))
    hist = docs[1]

    vals = hist["dependent_variables"][0]["values"]
    for i in range(len(vals)):
        vals[i] = {"value": float(f"{yields[i]:.4f}")}

    with open(str(RESULTS_YAML), 'w') as f:
        yaml.dump(docs[0], f, default_flow_style=False, sort_keys=False)
        f.write("---\n")
        yaml.dump(docs[1], f, default_flow_style=False, sort_keys=False)

    print(f"\nResults written to {RESULTS_YAML}")


if __name__ == "__main__":
    yields, counts = run_analysis()
    update_yaml(yields)
    print("\nFinal yields:")
    for (lo, hi), y in zip([(250,350),(350,450),(450,550),(550,650)], yields):
        print(f"  MET [{lo},{hi}): {y:.4f}")
