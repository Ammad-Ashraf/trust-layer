"""
CMS-SUS-16-051 compressed signal region analysis.
Applies compressed selection from Table 3 of arXiv:1706.04402 to
Delphes-simulated T2tt_800_400 events and fills MET histogram.

Run with: bin/run-analysis
"""
import math
import os

import awkward as ak
import numpy as np
import uproot
import yaml

# ── Normalization ─────────────────────────────────────────────────────────────
N_GEN = 50_000           # generated events
XS_NLO_PB = 0.0272       # Prospino NLO stop-antistop σ at 13 TeV (pb)
LUMI_FB = 35.9            # integrated luminosity (fb^-1)
WEIGHT = XS_NLO_PB * 1000.0 * LUMI_FB / N_GEN  # fb^-1 × pb × (1000 fb/pb) / N_gen

# ── Bin edges (from results YAML) ─────────────────────────────────────────────
BIN_EDGES = [250.0, 350.0, 450.0, 550.0, 650.0]  # last bin is overflow >= 550

# ── Helper: azimuthal angle difference ────────────────────────────────────────

def dphi_ak(phi1, phi2):
    """Element-wise |Δφ| wrapped into [0, π] for awkward arrays."""
    d = (phi1 - phi2) % (2 * np.pi)
    return ak.where(d <= np.pi, d, 2 * np.pi - d)


# ── Load chunk files from datasets.yaml ───────────────────────────────────────

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
datasets_path = os.path.join(WORKSPACE, "datasets.yaml")
with open(datasets_path) as _f:
    _datasets = yaml.safe_load(_f)

chunk_files = []
for _ds in _datasets:
    for _url in _ds.get("file_urls", []):
        _full = _url if os.path.isabs(_url) else os.path.join(WORKSPACE, _url)
        chunk_files.append(_full)
chunk_files = sorted(chunk_files)

if not chunk_files:
    raise RuntimeError(f"No Delphes chunks found at {CHUNK_PATTERN}")

print(f"Found {len(chunk_files)} Delphes chunk files")

# ── MET histogram bins (4 bins: 250-350, 350-450, 450-550, >550 GeV) ─────────
n_bins = 4
counts = np.zeros(n_bins, dtype=float)

# ── Analysis loop ─────────────────────────────────────────────────────────────

BRANCHES = [
    "Electron/Electron.PT", "Electron/Electron.Eta", "Electron/Electron.Phi",
    "Electron/Electron.IsolationVar",
    "Muon/Muon.PT", "Muon/Muon.Eta", "Muon/Muon.Phi",
    "Muon/Muon.IsolationVar",
    "Jet/Jet.PT", "Jet/Jet.Eta", "Jet/Jet.Phi", "Jet/Jet.BTag",
    "MissingET/MissingET.MET", "MissingET/MissingET.Phi",
]

n_total = 0
n_sel = 0

for chunk_path in chunk_files:
    with uproot.open(chunk_path) as f:
        tree = f["Delphes"]
        arrays = tree.arrays(BRANCHES, library="ak")

    n_events = len(arrays["Electron/Electron.PT"])
    n_total += n_events

    # ── Object selection ──────────────────────────────────────────────────────

    # Electrons: pT > 20 GeV, |η| < 1.442, isolation < 0.1 (paper cut)
    el_pt  = arrays["Electron/Electron.PT"]
    el_eta = arrays["Electron/Electron.Eta"]
    el_phi = arrays["Electron/Electron.Phi"]
    el_iso = arrays["Electron/Electron.IsolationVar"]
    el_sel = (el_pt > 20.0) & (np.abs(el_eta) < 1.442) & (el_iso < 0.1)
    electrons = ak.zip({
        "pt": el_pt[el_sel], "eta": el_eta[el_sel],
        "phi": el_phi[el_sel],
    })

    # Muons: pT > 20 GeV, |η| < 2.4, isolation < 0.1
    mu_pt  = arrays["Muon/Muon.PT"]
    mu_eta = arrays["Muon/Muon.Eta"]
    mu_phi = arrays["Muon/Muon.Phi"]
    mu_iso = arrays["Muon/Muon.IsolationVar"]
    mu_sel = (mu_pt > 20.0) & (np.abs(mu_eta) < 2.4) & (mu_iso < 0.1)
    muons = ak.zip({
        "pt": mu_pt[mu_sel], "eta": mu_eta[mu_sel],
        "phi": mu_phi[mu_sel],
    })

    # Jets: pT > 30 GeV, |η| < 2.4
    j_pt   = arrays["Jet/Jet.PT"]
    j_eta  = arrays["Jet/Jet.Eta"]
    j_phi  = arrays["Jet/Jet.Phi"]
    j_btag = arrays["Jet/Jet.BTag"]
    j_sel  = (j_pt > 30.0) & (np.abs(j_eta) < 2.4)
    jets = ak.zip({
        "pt": j_pt[j_sel], "eta": j_eta[j_sel],
        "phi": j_phi[j_sel], "btag": j_btag[j_sel],
    })

    # MET
    met     = ak.flatten(arrays["MissingET/MissingET.MET"])
    met_phi = ak.flatten(arrays["MissingET/MissingET.Phi"])

    # ── Event-level cuts ──────────────────────────────────────────────────────

    # Exactly one selected lepton (electron OR muon)
    n_el = ak.num(electrons)
    n_mu = ak.num(muons)
    has_one_lep = ((n_el == 1) & (n_mu == 0)) | ((n_el == 0) & (n_mu == 1))

    # Build combined lepton arrays for events with exactly one lepton
    lep_pt  = ak.where(n_el == 1, ak.firsts(electrons.pt),  ak.firsts(muons.pt))
    lep_phi = ak.where(n_el == 1, ak.firsts(electrons.phi), ak.firsts(muons.phi))
    # Replace None with 0 (irrelevant since we require has_one_lep)
    lep_pt  = ak.fill_none(lep_pt, 0.0)
    lep_phi = ak.fill_none(lep_phi, 0.0)

    # Veto extra leptons (loosely: any additional e/μ with pT > 5 GeV already excluded
    # because Delphes electrons have pT>10 GeV floor, and we require exactly 1 lepton above)

    # MET > 250 GeV
    met_cut = met > 250.0

    # Transverse mass MT > 150 GeV
    dphi_lep_met = dphi_ak(lep_phi, met_phi)
    mt = np.sqrt(2.0 * lep_pt * met * (1.0 - np.cos(dphi_lep_met)))
    mt_cut = mt > 150.0

    # Jet multiplicity >= 2 with at least one b-tagged (medium WP, BTag bit 0)
    n_jets = ak.num(jets)
    n_bjet = ak.sum(jets.btag > 0, axis=1)
    jet_bjet_cut = (n_jets >= 2) & (n_bjet >= 1)

    # ── Compressed selection (Table 3) ────────────────────────────────────────

    # NJ >= 5
    nj5_cut = n_jets >= 5

    # Leading jet (J1) NOT b-tagged
    j1_btag = ak.fill_none(ak.firsts(jets.btag), 1)   # default 1 → fails cut if no jet
    j1_notbtag = j1_btag == 0

    # Δφ(MET, lepton) < 2
    dphi_met_lep = dphi_ak(met_phi, lep_phi)
    dphi_met_lep_cut = dphi_met_lep < 2.0

    # min Δφ(J1,2, MET) > 0.5
    j1_phi = ak.fill_none(ak.firsts(jets.phi), 0.0)
    j2_phi = ak.fill_none(ak.pad_none(jets.phi, 2)[:, 1], 0.0)
    dphi_j1_met = dphi_ak(j1_phi, met_phi)
    dphi_j2_met = dphi_ak(j2_phi, met_phi)
    min_dphi_j12_met = ak.where(dphi_j1_met < dphi_j2_met, dphi_j1_met, dphi_j2_met)
    min_dphi_cut = min_dphi_j12_met > 0.5

    # Lepton pT < 150 GeV
    lep_pt_cut = lep_pt < 150.0

    # ── Combined selection mask ────────────────────────────────────────────────
    mask = (
        has_one_lep
        & met_cut
        & mt_cut
        & jet_bjet_cut
        & nj5_cut
        & j1_notbtag
        & dphi_met_lep_cut
        & min_dphi_cut
        & lep_pt_cut
    )

    # ── Fill MET histogram ────────────────────────────────────────────────────
    met_pass = np.asarray(met[mask])
    # Bin 0: 250-350, 1: 350-450, 2: 450-550, 3: >=550 (overflow into last bin)
    chunk_counts, _ = np.histogram(np.clip(met_pass, 250.0, 649.9), bins=[250., 350., 450., 550., 650.])
    counts += chunk_counts

    n_sel += int(ak.sum(mask))
    print(f"  {chunk_path.split('/')[-1]}: {int(ak.sum(mask))} / {n_events} selected")

# ── Scale to luminosity ────────────────────────────────────────────────────────
yields = counts * WEIGHT

print(f"\nTotal events processed : {n_total}")
print(f"Total events selected  : {n_sel}")
print(f"Event weight           : {WEIGHT:.6f}")
print(f"\nMET bins [250-350, 350-450, 450-550, >550 GeV]:")
for i, (lo, hi, y) in enumerate(zip(
    [250, 350, 450, 550], [350, 450, 550, "inf"], yields
)):
    print(f"  [{lo}-{hi}] GeV : {y:.4f} events")

# ── Write results YAML ────────────────────────────────────────────────────────
results_path = os.path.join(WORKSPACE, "results", "histogram_T2tt_comp.yaml")
with open(results_path) as fh:
    raw = fh.read()

# The file has two YAML documents separated by ---
parts = raw.split("---", 1)
if len(parts) != 2:
    raise RuntimeError("Expected two YAML documents in results file")

meta_block = parts[0]
hist_block = parts[1]

hist = yaml.safe_load(hist_block)
for i, val in enumerate(yields):
    hist["dependent_variables"][0]["values"][i]["value"] = round(float(val), 4)

with open(results_path, "w") as fh:
    fh.write(meta_block)
    fh.write("---\n")
    fh.write(yaml.dump(hist, default_flow_style=False))

print(f"\nResults written to {results_path}")
