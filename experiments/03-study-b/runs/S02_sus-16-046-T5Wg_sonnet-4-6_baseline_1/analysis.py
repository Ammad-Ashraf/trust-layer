"""
CMS-SUS-16-046 signal analysis for T5Wg_1750_1700.
Applies full event selection from Table 1 of the paper and fills S_T^gamma histogram.

Selection:
  Preselection:
    - MET filters (skipped: not applicable in Delphes MC)
    - >= 1 vertex (always satisfied in Delphes)
    - >= 1 photon: pT > 180 GeV, |eta| < 1.44
    - DeltaR(gamma, jet) > 0.5 (for nearest jet)
    - DeltaPhi(MET, jet) > 0.3 for all jets with pT > 100 GeV

  Signal region:
    - MET > 300 GeV
    - MT(gamma_1, MET) > 300 GeV  (gamma_1 = highest-pT photon)
    - S_T^gamma = MET + sum_gamma pT(gamma) > 600 GeV

  Bin edges (from histogram template): [600, 800, 1000, 1300, 1600 GeV]
  Last bin (>1300) is overflow-inclusive.

Normalization:
  - sigma_NLO (gluino pair, m=1750 GeV) = 2.68 fb (Prospino)
  - Luminosity = 35.9 fb^-1
  - Trigger efficiency = 94.3%
  - Photon LoosePixelVeto efficiency from histogram (per photon)
"""

import numpy as np
import uproot
import awkward as ak
import yaml

WORKSPACE = "/home/israr/Documents/Ammad-Particle-Physics/trust-layer/external/collider-bench/runs/claude_sonnet-4-6/sus-16-046_sim-T5Wg_JollyNewton_72f722a4/workspace"

DELPHES_FILE = f"{WORKSPACE}/sims/delphes_output_v2.root"
EFF_FILE     = f"{WORKSPACE}/object_efficiencies/photon_eff_LoosePixelVeto.root"
YAML_FILE    = f"{WORKSPACE}/results/histogram_T5Wg.yaml"
DATA_OUT     = f"{WORKSPACE}/data/selected_T5Wg.root"

N_GENERATED  = 20000
SIGMA_NLO_FB = 2.68          # Prospino NLO, gluino pair, m=1750 GeV, 13 TeV
LUMI_FB      = 35.9
TRIG_EFF     = 0.943          # trigger efficiency (pT>165 GeV single-photon trigger)

# --- Photon efficiency (LoosePixelVeto) ----------------------------------------
# Bins: x=|eta| {(0,0.8), (0.8,1.4442), (1.566,2.0), (2.0,2.5)}
#        y=ET   {20-35,  35-50,  50-90,  90-500 GeV}
EFF_ETA_EDGES = [0.0, 0.8, 1.4442, 1.566, 2.0, 2.5]  # bin edges in eta
EFF_ET_EDGES  = [20., 35., 50., 90., 500.]             # bin edges in ET (GeV)

with uproot.open(EFF_FILE) as f:
    eff_vals, eff_x, eff_y = f["PhotonEfficiency"].to_numpy()
# eff_vals[i_eta, i_et] where i_eta, i_et are 0-3

def photon_eff(pt, abseta):
    """Return LoosePixelVeto efficiency for a photon with given pT and |eta|."""
    # Map |eta| to bin index (using the labels found in the histogram)
    eta_boundaries = [0.0, 0.8, 1.4442, 2.0, 2.5]
    i_eta = np.searchsorted(eta_boundaries[1:], abseta, side='right')
    i_eta = np.clip(i_eta, 0, 3)

    # Map ET to bin index
    et_boundaries = [20., 35., 50., 90., 500.]
    i_et = np.searchsorted(et_boundaries[1:], pt, side='right')
    i_et = np.clip(i_et, 0, 3)

    return eff_vals[i_eta, i_et]

# --- Load Delphes output --------------------------------------------------------
print(f"Opening {DELPHES_FILE}")
tree = uproot.open(DELPHES_FILE)["Delphes"]
print(f"Total events: {tree.num_entries}")

ph_pt   = tree["Photon/Photon.PT"].array(library="ak")
ph_eta  = tree["Photon/Photon.Eta"].array(library="ak")
ph_phi  = tree["Photon/Photon.Phi"].array(library="ak")
met_pt  = tree["MissingET/MissingET.MET"].array(library="ak")
met_phi = tree["MissingET/MissingET.Phi"].array(library="ak")
jet_pt  = tree["Jet/Jet.PT"].array(library="ak")
jet_eta = tree["Jet/Jet.Eta"].array(library="ak")
jet_phi = tree["Jet/Jet.Phi"].array(library="ak")

# MET per event (single value per event)
MET   = ak.flatten(met_pt)
MET_phi = ak.flatten(met_phi)

# --- Helper: delta_phi (folded to [-pi, pi]) ------------------------------------
def delta_phi(phi1, phi2):
    dphi = phi1 - phi2
    return dphi - 2 * np.pi * np.round(dphi / (2 * np.pi))

def delta_r(eta1, phi1, eta2, phi2):
    return np.sqrt((eta1 - eta2)**2 + delta_phi(phi1, phi2)**2)

# --- Step 1: Photon selection ---------------------------------------------------
# Select photons: pT > 180, |eta| < 1.44 (barrel)
mask_ph = (ph_pt > 180.0) & (np.abs(ph_eta) < 1.44)

# Count selected photons per event
n_selected_ph = ak.sum(mask_ph, axis=1)
# Require >= 1 selected photon
pass_photon = n_selected_ph >= 1

# Get the leading (highest-pT) selected photon per event
sel_ph_pt  = ph_pt[mask_ph]
sel_ph_eta = ph_eta[mask_ph]
sel_ph_phi = ph_phi[mask_ph]

# Sort by pT descending to get leading photon
sort_idx = ak.argsort(sel_ph_pt, axis=1, ascending=False)
sel_ph_pt  = sel_ph_pt[sort_idx]
sel_ph_eta = sel_ph_eta[sort_idx]
sel_ph_phi = sel_ph_phi[sort_idx]

# Leading photon (pT, eta, phi) — padded for events with no photon
lead_ph_pt  = ak.pad_none(sel_ph_pt[:, :1], 1, axis=1)[:, 0]
lead_ph_eta = ak.pad_none(sel_ph_eta[:, :1], 1, axis=1)[:, 0]
lead_ph_phi = ak.pad_none(sel_ph_phi[:, :1], 1, axis=1)[:, 0]

lead_ph_pt  = ak.fill_none(lead_ph_pt, 0.0)
lead_ph_eta = ak.fill_none(lead_ph_eta, 0.0)
lead_ph_phi = ak.fill_none(lead_ph_phi, 0.0)

# --- Step 2: DeltaR(gamma, jet) > 0.5 ------------------------------------------
# For each event: compute min DeltaR between leading photon and all jets
# (require > 0.5 from nearest jet)
# Using broadcast: for each event, compute DeltaR to all jets
n_ev = len(ph_pt)
# Build per-event DeltaR arrays between leading photon and all jets
# Note: lead_ph_eta/phi are per-event scalars

# Broadcast: lead_ph_eta has shape (n_ev,), jet_eta has shape (n_ev, n_jets)
dR_ph_jet = delta_r(
    lead_ph_eta[:, np.newaxis] * ak.ones_like(jet_eta),
    lead_ph_phi[:, np.newaxis] * ak.ones_like(jet_phi),
    jet_eta,
    jet_phi
)

# Min DeltaR to any jet
min_dR_ph_jet = ak.where(
    ak.num(dR_ph_jet) > 0,
    ak.min(dR_ph_jet, axis=1),
    999.0
)
pass_dr_ph_jet = (min_dR_ph_jet > 0.5) | pass_photon  # only matters if photon exists

# Actually compute properly: only require DeltaR > 0.5 if the event has photon AND jets
# If no jets, the cut is trivially passed
pass_dr_ph_jet_cut = ak.where(
    ak.num(jet_pt) > 0,
    min_dR_ph_jet > 0.5,
    True
)

# --- Step 3: DeltaPhi(MET, jet) > 0.3 for jets with pT > 100 GeV ---------------
hard_jets_mask = jet_pt > 100.0
hard_jet_phi = jet_phi[hard_jets_mask]

dphi_met_jet = np.abs(delta_phi(
    MET_phi[:, np.newaxis] * ak.ones_like(hard_jet_phi),
    hard_jet_phi
))

min_dphi = ak.where(
    ak.num(hard_jet_phi) > 0,
    ak.min(dphi_met_jet, axis=1),
    999.0
)
pass_dphi_cut = (min_dphi > 0.3) | (ak.num(hard_jet_phi) == 0)

# --- Step 4: Signal region cuts -------------------------------------------------
pass_met_cut = MET > 300.0

# MT(gamma_1, MET) = sqrt(2 * pT_g * MET * (1 - cos(dphi)))
dphi_lead_met = np.abs(delta_phi(lead_ph_phi, MET_phi))
MT = np.sqrt(2.0 * lead_ph_pt * MET * (1.0 - np.cos(dphi_lead_met)))
pass_mt_cut = MT > 300.0

# S_T^gamma = MET + sum of all selected photon pT
sum_ph_pt = ak.sum(sel_ph_pt, axis=1)
ST_gamma = MET + sum_ph_pt
pass_st_cut = ST_gamma > 600.0

# --- Combine all preselection + signal region -----------------------------------
pass_sel = (
    pass_photon &
    pass_dr_ph_jet_cut &
    pass_dphi_cut &
    pass_met_cut &
    pass_mt_cut &
    pass_st_cut
)
pass_sel_np = np.asarray(pass_sel)
n_pass_sel = int(np.sum(pass_sel_np))
print(f"Events passing full signal region selection: {n_pass_sel}/{N_GENERATED}")

# --- Compute event weights ------------------------------------------------------
# Photon LoosePixelVeto efficiency (use leading barrel photon)
lead_pt_np  = np.asarray(lead_ph_pt)
lead_eta_np = np.asarray(np.abs(lead_ph_eta))

ph_eff = np.where(
    pass_sel_np,
    np.vectorize(photon_eff)(lead_pt_np, lead_eta_np),
    0.0
)

# Combined per-event weight (trigger eff × photon ID eff)
event_weight = np.where(pass_sel_np, TRIG_EFF * ph_eff, 0.0)

# Normalization scale factor
# N_signal = (N_gen_weighted / N_gen_total) * sigma_NLO * L
# Here each MC event has weight = 1/N_gen_total at generation
scale = SIGMA_NLO_FB * LUMI_FB  # expected events = sigma × L × eff

eff_weighted = np.sum(event_weight[pass_sel_np]) / N_GENERATED
print(f"Weighted efficiency (incl. trigger+ID): {eff_weighted:.4f}")
print(f"Expected signal events: {scale * eff_weighted:.2f}")

# Signal yield per event (for histogram)
yield_per_event = event_weight * scale / N_GENERATED

# --- Fill S_T^gamma histogram ---------------------------------------------------
st_np = np.asarray(ST_gamma)
bin_edges = [600., 800., 1000., 1300., 1600.]  # 4 bins, last is overflow-inclusive

# Bin the selected events
yields = np.zeros(4)
for i in range(4):
    lo = bin_edges[i]
    hi = bin_edges[i + 1]
    if i == 3:  # overflow: include all events >= 1300
        in_bin = pass_sel_np & (st_np >= lo)
    else:
        in_bin = pass_sel_np & (st_np >= lo) & (st_np < hi)
    yields[i] = np.sum(yield_per_event[in_bin])

print("\nS_T^gamma histogram (expected yields at 35.9 fb^-1):")
for i, (lo, hi, y) in enumerate(zip(bin_edges[:-1], bin_edges[1:], yields)):
    label = f">={lo:.0f}" if i == 3 else f"[{lo:.0f},{hi:.0f})"
    print(f"  {label} GeV: {y:.3f}")

# --- Write output YAML ----------------------------------------------------------
with open(YAML_FILE) as f:
    raw = f.read()

# Split at --- separator
parts = raw.split("---\n", 1)
meta_block = parts[0]
histo_block = parts[1]

histo = yaml.safe_load(histo_block)
for i, val in enumerate(yields):
    histo["dependent_variables"][0]["values"][i]["value"] = round(float(val), 4)

with open(YAML_FILE, "w") as f:
    f.write(meta_block)
    f.write("---\n")
    yaml.dump(histo, f, default_flow_style=None, sort_keys=False)

print(f"\nHistogram written to {YAML_FILE}")

# --- Save selected events to ROOT for data directory ----------------------------
import ROOT
ROOT.gROOT.SetBatch(True)

outf = ROOT.TFile(DATA_OUT, "RECREATE")
t = ROOT.TTree("SelectedEvents", "Selected T5Wg signal events")

arr_met    = np.zeros(1, dtype=np.float32)
arr_st     = np.zeros(1, dtype=np.float32)
arr_mt     = np.zeros(1, dtype=np.float32)
arr_ph_pt  = np.zeros(1, dtype=np.float32)
arr_wt     = np.zeros(1, dtype=np.float32)

t.Branch("MET",     arr_met,    "MET/F")
t.Branch("ST_gamma",arr_st,     "ST_gamma/F")
t.Branch("MT",      arr_mt,     "MT/F")
t.Branch("lead_ph_pt", arr_ph_pt, "lead_ph_pt/F")
t.Branch("weight",  arr_wt,     "weight/F")

met_np = np.asarray(MET)
mt_np  = np.asarray(MT)

for i in range(N_GENERATED):
    if pass_sel_np[i]:
        arr_met[0]   = float(met_np[i])
        arr_st[0]    = float(st_np[i])
        arr_mt[0]    = float(mt_np[i])
        arr_ph_pt[0] = float(lead_pt_np[i])
        arr_wt[0]    = float(yield_per_event[i])
        t.Fill()

outf.Write()
outf.Close()
print(f"Selected events saved to {DATA_OUT}")
print("Done.")
