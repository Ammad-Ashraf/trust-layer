"""CMS-SUS-16-046 T5Wg signal analysis.

Event selection from Table 1 of CMS-SUS-16-046:
  photon pT > 180 GeV, |eta| < 1.44, DR(gamma,jet) > 0.5
  Dphi(MET, hard jet) > 0.3 for jets pT > 100 GeV
  MET > 300 GeV, MT(gamma, MET) > 300 GeV, S_T^gamma > 600 GeV

Input: data/delphes_output.root (from datasets.yaml)
Output: results/histogram_T5Wg.yaml (four S_T^gamma bins)
"""
import os
import numpy as np
import awkward as ak
import uproot
import yaml

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
PHOTON_EFF_FILE = os.path.join(WORKSPACE, "object_efficiencies", "photon_eff_LoosePixelVeto.root")
RESULTS_YAML = os.path.join(WORKSPACE, "results", "histogram_T5Wg.yaml")

SIGMA_NLO_FB  = 2.68    # fb, Prospino NLO, m(g~)=1750 GeV, 13 TeV
LUMINOSITY_FB = 35.9    # fb^-1
N_GEN         = 50000   # LHE events generated (pp->g~g~)
EVENT_WEIGHT  = SIGMA_NLO_FB * LUMINOSITY_FB / N_GEN
TRIGGER_EFF   = 0.943   # CMS-SUS-16-046 single-photon trigger efficiency
BIN_EDGES     = np.array([600.0, 800.0, 1000.0, 1300.0, 1600.0])  # 4 bins


def _dphi_norm(phi):
    return (phi + np.pi) % (2.0 * np.pi) - np.pi


def run():
    with open("datasets.yaml") as f:
        datasets = yaml.safe_load(f)
    sig_ds = next(d for d in datasets if d.get("role") == "signal")
    input_path = sig_ds["file_urls"][0]
    print(f"Input: {input_path}")

    with uproot.open(PHOTON_EFF_FILE) as feff:
        heff = feff["PhotonEfficiency;1"]
        eff_vals, xedges, yedges = heff.to_numpy()
    print(f"Photon efficiency map: shape {eff_vals.shape}, |eta| edges {xedges}")

    with uproot.open(input_path) as f:
        tree = f["Delphes"]
        photon_pt  = tree["Photon/Photon.PT"].array()
        photon_eta = tree["Photon/Photon.Eta"].array()
        photon_phi = tree["Photon/Photon.Phi"].array()
        met_raw    = tree["MissingET/MissingET.MET"].array()
        met_phi_raw = tree["MissingET/MissingET.Phi"].array()
        jet_pt     = tree["Jet/Jet.PT"].array()
        jet_eta    = tree["Jet/Jet.Eta"].array()
        jet_phi    = tree["Jet/Jet.Phi"].array()

    met     = ak.fill_none(ak.firsts(met_raw),     0.0)
    met_phi = ak.fill_none(ak.firsts(met_phi_raw), 0.0)
    n_total = len(photon_pt)
    print(f"Total events: {n_total}")

    # --- Photon preselection: pT > 180 GeV, barrel |eta| < 1.44 ---
    phot_base = (photon_pt > 180.0) & (np.abs(photon_eta) < 1.44)
    ph_pt_b  = photon_pt[phot_base]
    ph_eta_b = photon_eta[phot_base]
    ph_phi_b = photon_phi[phot_base]

    # --- DR(gamma, jet) isolation > 0.5 ---
    ph_rec = ak.zip({"eta": ph_eta_b, "phi": ph_phi_b})
    j_rec  = ak.zip({"eta": jet_eta,  "phi": jet_phi})
    combos = ak.cartesian({"ph": ph_rec, "j": j_rec}, nested=True)
    deta = combos["ph"]["eta"] - combos["j"]["eta"]
    dphi = _dphi_norm(combos["ph"]["phi"] - combos["j"]["phi"])
    dr   = np.sqrt(deta**2 + dphi**2)
    min_dr = ak.fill_none(ak.min(dr, axis=2), 999.0)
    isolated = min_dr > 0.5

    good_ph_pt  = ph_pt_b[isolated]
    good_ph_eta = ph_eta_b[isolated]
    good_ph_phi = ph_phi_b[isolated]
    has_photon  = ak.num(good_ph_pt) >= 1

    # --- Dphi(MET, hard jet) > 0.3 for jets pT > 100 GeV ---
    hj_phi = jet_phi[jet_pt > 100.0]
    # Broadcast met_phi ([n_events]) over jet axis ([n_events][n_jets])
    met_phi_bc, _ = ak.broadcast_arrays(met_phi, hj_phi)
    dphi_mj   = np.abs(_dphi_norm(hj_phi - met_phi_bc))
    min_dphi  = ak.fill_none(ak.min(dphi_mj, axis=1), 999.0)
    dphi_ok   = min_dphi > 0.3

    # --- Signal region cuts ---
    met_cut = met > 300.0

    lead_pt  = ak.fill_none(ak.firsts(good_ph_pt),  0.0)
    lead_phi = ak.fill_none(ak.firsts(good_ph_phi), 0.0)
    lead_eta = ak.fill_none(ak.firsts(good_ph_eta), 0.0)
    mt = np.sqrt(2.0 * lead_pt * met * (1.0 - np.cos(_dphi_norm(lead_phi - met_phi))))
    mt_cut = mt > 300.0

    st     = met + ak.sum(good_ph_pt, axis=1)
    st_cut = st >= 600.0

    sel = has_photon & dphi_ok & met_cut & mt_cut & st_cut
    n_sel = int(ak.sum(sel))
    print(f"After preselection (photon + dphi_ok): {int(ak.sum(has_photon & dphi_ok))}")
    print(f"After signal region (MET+MT+ST):        {n_sel}")

    if n_sel == 0:
        print("WARNING: no events pass signal selection")
        return np.zeros(4)

    # --- Photon efficiency (vectorized) ---
    sel_eta = np.asarray(lead_eta[sel])
    ix = np.clip(np.searchsorted(xedges, np.abs(sel_eta), side="right") - 1,
                 0, len(xedges) - 2)
    iy = np.full(n_sel, len(yedges) - 2)  # highest ET bin
    ph_eff  = eff_vals[ix, iy]
    weights = EVENT_WEIGHT * ph_eff * TRIGGER_EFF

    # --- S_T^gamma histogram ---
    sel_st  = ak.to_numpy(st[sel]).astype(float)
    bin_idx = np.clip(np.digitize(sel_st, BIN_EDGES) - 1, 0, 3)
    hist    = np.zeros(4)
    hist_sq = np.zeros(4)
    np.add.at(hist,    bin_idx, weights)
    np.add.at(hist_sq, bin_idx, weights**2)

    print(f"\nS_T^gamma signal yields at {LUMINOSITY_FB} fb^-1:")
    for b, (lo, hi) in enumerate(zip(BIN_EDGES[:-1], BIN_EDGES[1:])):
        print(f"  [{lo:.0f}, {hi:.0f}] GeV: {hist[b]:.4f} ± {np.sqrt(hist_sq[b]):.4f}")
    print(f"  Total signal: {np.sum(hist):.4f}")
    return hist


def update_results(hist):
    with open(RESULTS_YAML, "r") as f:
        content = f.read()
    parts = content.split("---\n", 1)
    hdata = yaml.safe_load(parts[1])
    for i, val in enumerate(hist):
        hdata["dependent_variables"][0]["values"][i]["value"] = round(float(val), 6)
    with open(RESULTS_YAML, "w") as f:
        f.write(parts[0])
        f.write("---\n")
        yaml.dump(hdata, f, default_flow_style=False, allow_unicode=True)
    print(f"Updated {RESULTS_YAML}")


if __name__ == "__main__":
    hist = run()
    update_results(hist)
    print("Analysis complete.")
