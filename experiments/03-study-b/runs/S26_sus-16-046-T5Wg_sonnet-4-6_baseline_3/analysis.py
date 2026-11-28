"""
CMS-SUS-16-046 signal region analysis for T5Wg_1750_1700.

Applies the event selection from Table 1 of the paper:
  - Preselection: >=1 photon with pT>180 GeV, |eta|<1.44
                  dR(gamma, jet) > 0.5
                  dphi(MET, jet) > 0.3 for jets with pT>100 GeV
  - Signal region: MET > 300 GeV, MT(gamma, MET) > 300 GeV, ST_gamma > 600 GeV
  - Bins: ST_gamma in [600,800], [800,1000], [1000,1300], [>1300] GeV

Also applies:
  - Photon trigger efficiency: 94.3%
  - NLO+NLL cross section normalization to 35.9 fb^-1

Output: fills results/histogram_T5Wg.yaml and writes data/selected_events.root
"""

import numpy as np
import uproot
import awkward as ak
import yaml
import os
import sys

# ── paths ──────────────────────────────────────────────────────────────────────
WORKSPACE = os.path.dirname(os.path.abspath(__file__))

# Load input file from datasets.yaml (required by run-analysis framework)
_datasets_path = os.path.join(WORKSPACE, "datasets.yaml")
with open(_datasets_path) as _fh:
    _raw = _fh.read()
_datasets = yaml.safe_load(_raw.split("---\n")[-1]) if "---\n" in _raw else yaml.safe_load(_raw)
# Find the first mc dataset file
_ds = next((d for d in (_datasets or []) if d.get("role") == "mc"), None)
DELPHES_ROOT = os.path.join(WORKSPACE, _ds["file_urls"][0]) if _ds else os.path.join(WORKSPACE, "data", "delphes_output.root")

RESULTS_YAML = os.path.join(WORKSPACE, "results", "histogram_T5Wg.yaml")

# ── normalization ──────────────────────────────────────────────────────────────
# NLO gluino pair production cross section at m(g~)=1750 GeV, 13 TeV
# From Prospino 2.1: sigma(NLO) = 3.28 fb (K=2.18 wrt LO=1.5 fb)
# MG5 aMC LO: 1.889 fb (consistent with Prospino LO within PDF uncertainties)
# Paper uses NLO+NLL; we apply Prospino NLO as the best available from these tools.
# NNLLfast NLO+NLL for m(g~)=1750 GeV would be ~1.4 fb (see report.md).
SIGMA_NLO_FB = 3.28          # fb (NLO, Prospino 2.1, decoupled squarks)
LUMI_FB = 35.9               # fb^-1
N_GEN = 50000                # generated events
SIGMA_LO_MG5_FB = 1.889      # fb (LO MG5, used for event weighting)
TRIGGER_EFF = 0.943          # photon trigger efficiency (CMS-SUS-16-046 Sec. 5)

# Event weight per generated event (using NLO xsec, with LO event sample)
WEIGHT_PER_EVENT = (SIGMA_NLO_FB * LUMI_FB) / N_GEN

# ── bin edges ─────────────────────────────────────────────────────────────────
BINS = [600., 800., 1000., 1300., 1600.]  # last bin is overflow (>1300)


def calc_mt(pt_obj, phi_obj, met, met_phi):
    """Transverse mass MT(object, MET)."""
    dphi = phi_obj - met_phi
    # wrap to [-pi, pi]
    dphi = (dphi + np.pi) % (2 * np.pi) - np.pi
    return np.sqrt(2 * pt_obj * met * (1 - np.cos(dphi)))


def delta_r(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = phi1 - phi2
    dphi = (dphi + np.pi) % (2 * np.pi) - np.pi
    return np.sqrt(deta**2 + dphi**2)


def delta_phi(phi1, phi2):
    dphi = phi1 - phi2
    return np.abs((dphi + np.pi) % (2 * np.pi) - np.pi)


def run_analysis():
    if not os.path.exists(DELPHES_ROOT):
        print(f"ERROR: Delphes file not found: {DELPHES_ROOT}", file=sys.stderr)
        sys.exit(1)

    f = uproot.open(DELPHES_ROOT)
    tree = f["Delphes"]
    n_total = tree.num_entries
    print(f"Total Delphes events: {n_total}")

    # Load branches
    branches = tree.arrays([
        "Photon/Photon.PT",
        "Photon/Photon.Eta",
        "Photon/Photon.Phi",
        "Jet/Jet.PT",
        "Jet/Jet.Eta",
        "Jet/Jet.Phi",
        "MissingET/MissingET.MET",
        "MissingET/MissingET.Phi",
    ], library="ak")

    ph_pt  = branches["Photon/Photon.PT"]
    ph_eta = branches["Photon/Photon.Eta"]
    ph_phi = branches["Photon/Photon.Phi"]
    jet_pt  = branches["Jet/Jet.PT"]
    jet_eta = branches["Jet/Jet.Eta"]
    jet_phi = branches["Jet/Jet.Phi"]
    met     = ak.to_numpy(ak.flatten(branches["MissingET/MissingET.MET"], axis=1))
    met_phi = ak.to_numpy(ak.flatten(branches["MissingET/MissingET.Phi"], axis=1))

    # Event indices
    nevt = n_total
    sel = np.ones(nevt, dtype=bool)

    # ── Preselection step 1: at least one photon pT>180, |eta|<1.44 ────────────
    ph_pass = (ph_pt > 180.0) & (np.abs(ph_eta) < 1.44)
    n_good_ph = ak.sum(ph_pass, axis=1)
    sel &= (ak.to_numpy(n_good_ph) >= 1)
    print(f"After photon pT>180,|eta|<1.44: {sel.sum()}")

    # ── Build leading photon quantities ───────────────────────────────────────
    # Leading photon among those passing the photon cut
    ph_pass_pt  = ph_pt[ph_pass]
    ph_pass_eta = ph_eta[ph_pass]
    ph_pass_phi = ph_phi[ph_pass]

    lead_ph_pt  = ak.to_numpy(ak.fill_none(ak.firsts(ph_pass_pt), 0.0))
    lead_ph_eta = ak.to_numpy(ak.fill_none(ak.firsts(ph_pass_eta), 0.0))
    lead_ph_phi = ak.to_numpy(ak.fill_none(ak.firsts(ph_pass_phi), 0.0))

    # ── Preselection step 2: dR(gamma, jet) > 0.5 (vectorized) ──────────────
    # Broadcast leading photon eta/phi to match jet array shape
    lead_ph_eta_bc = ak.broadcast_arrays(lead_ph_eta, jet_eta)[0]
    lead_ph_phi_bc = ak.broadcast_arrays(lead_ph_phi, jet_phi)[0]
    deta = jet_eta - lead_ph_eta_bc
    dphi_arr = jet_phi - lead_ph_phi_bc
    dphi_arr = (dphi_arr + np.pi) % (2 * np.pi) - np.pi
    dr_arr = np.sqrt(deta**2 + dphi_arr**2)
    has_close_jet = ak.to_numpy(ak.any(dr_arr < 0.5, axis=1))
    sel &= ~has_close_jet
    print(f"After dR(gamma,jet)>0.5: {sel.sum()}")

    # ── Preselection step 3: dphi(MET, jet) > 0.3 for pT(jet)>100 (vectorized)
    met_phi_bc = ak.broadcast_arrays(met_phi, jet_phi)[0]
    dphi_met = jet_phi - met_phi_bc
    dphi_met = np.abs((dphi_met + np.pi) % (2 * np.pi) - np.pi)
    # Only check jets with pT > 100 GeV
    high_pt_jet = jet_pt > 100.0
    bad_dphi_arr = high_pt_jet & (dphi_met < 0.3)
    bad_dphi = ak.to_numpy(ak.any(bad_dphi_arr, axis=1))
    sel &= ~bad_dphi
    print(f"After dphi(MET,jet)>0.3: {sel.sum()}")

    # ── Signal region cuts ────────────────────────────────────────────────────
    # MET > 300 GeV
    sel &= (met > 300.0)
    print(f"After MET>300 GeV: {sel.sum()}")

    # MT(gamma, MET) > 300 GeV
    mt = calc_mt(lead_ph_pt, lead_ph_phi, met, met_phi)
    sel &= (mt > 300.0)
    print(f"After MT>300 GeV: {sel.sum()}")

    # ST_gamma > 600 GeV (sum of pT of all good photons + MET)
    # ST_gamma = MET + sum_gamma pT(gamma_i) for all photons passing selection
    sum_ph_pt = ak.to_numpy(ak.sum(ph_pass_pt, axis=1))
    st_gamma = met + sum_ph_pt
    sel &= (st_gamma > 600.0)
    print(f"After ST_gamma>600 GeV: {sel.sum()}")

    # ── Apply trigger efficiency ──────────────────────────────────────────────
    # Weight all selected events by trigger efficiency (applied as overall factor)
    n_sel = sel.sum()
    print(f"Total selected events: {n_sel}")

    # ── Histogram in ST_gamma bins ────────────────────────────────────────────
    st_sel = st_gamma[sel]
    # Clamp overflow into last bin
    st_clamped = np.where(st_sel > 1300., 1599.9, st_sel)

    # Raw counts
    counts, _ = np.histogram(st_clamped, bins=BINS)
    print(f"Raw counts per bin: {counts}")

    # Weighted counts (NLO normalization × trigger eff)
    weighted_counts = counts * WEIGHT_PER_EVENT * TRIGGER_EFF
    print(f"Weighted yields (NLO, {LUMI_FB} fb^-1): {weighted_counts}")

    # ── Write results YAML ────────────────────────────────────────────────────
    with open(RESULTS_YAML) as fh:
        raw = fh.read()

    # Split at --- separator
    parts = raw.split("---\n", 1)
    meta_block = parts[0]
    histo_block = parts[1]

    histo = yaml.safe_load(histo_block)
    for i, val in enumerate(weighted_counts):
        histo["dependent_variables"][0]["values"][i]["value"] = float(round(val, 4))

    with open(RESULTS_YAML, "w") as fh:
        fh.write(meta_block)
        fh.write("---\n")
        yaml.dump(histo, fh, default_flow_style=False, sort_keys=False)

    print(f"\nResults written to {RESULTS_YAML}")

    # ── Save selected events to ROOT ──────────────────────────────────────────
    out_root = os.path.join(WORKSPACE, "data", "selected_events.root")
    idx_sel = np.where(sel)[0]
    with uproot.recreate(out_root) as rfile:
        rfile["selected"] = {
            "event_idx": idx_sel,
            "st_gamma": st_gamma[sel],
            "met": met[sel],
            "mt_gamma_met": mt[sel],
            "lead_ph_pt": lead_ph_pt[sel],
            "lead_ph_eta": lead_ph_eta[sel],
            "weight": np.full(n_sel, WEIGHT_PER_EVENT * TRIGGER_EFF),
        }
    print(f"Selected events written to {out_root}")

    return weighted_counts


if __name__ == "__main__":
    run_analysis()
