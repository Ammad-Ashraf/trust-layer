"""
CMS-SUS-16-051 Compressed Signal Region Analysis
=================================================
Implements the compressed selection (Table 3) of CMS-SUS-16-051 and fills
the MET histogram for T2tt_800_400 (m_stop=800 GeV, m_LSP=400 GeV).

Compressed selection (preselection from Table 1 + Table 3 requirements):

Preselection (Table 1, with relaxed min_dphi for compressed):
  - Exactly 1 lepton (e: pT>20 GeV, |eta|<2.1; mu: pT>20, |eta|<2.4)
  - >=2 jets pT>30 GeV, |eta|<2.4
  - >=1 b-tagged jet (medium WP, Delphes BTag bit 0)
  - MET > 250 GeV
  - min_dphi(MET, J1or2) > 0.5  [relaxed from 0.8 for compressed region]
  - MT > 150 GeV
  - Veto: no additional leptons pT>5 GeV
  - Veto: no isolated tracks pT>10 GeV (simplified)

Compressed additional cuts (Table 3):
  - NJ >= 5
  - J1 (highest pT) NOT b-tagged
  - dphi(MET, lepton) < 2
  - pT^lep < 150 GeV

Signal regions:
  MET = [250,350], [350,450], [450,550], >550 GeV
"""

import os
import sys
import math
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKSPACE    = os.path.dirname(os.path.abspath(__file__))
DELPHES_FILE = os.path.join(WORKSPACE, "data", "delphes_T2tt_800_400.root")
RESULTS_FILE = os.path.join(WORKSPACE, "results", "histogram_T2tt_comp.yaml")
DELPHES_DIR  = "/opt/sim/delphes"

# ---------------------------------------------------------------------------
# Normalization constants
# ---------------------------------------------------------------------------
XS_NLO_PB = 0.0272     # pb (Prospino NLO, m_stop=800 GeV)
XS_LO_PB  = 0.0159     # pb (Prospino LO, for reference)
LUMI_FB   = 35.9       # fb^-1 (CMS 2016 dataset)
N_GEN     = 50000      # generated events (MG5)
# weight per event = sigma_NLO [pb] * lumi [fb^-1] * 1000 [fb/pb] / N_gen
EVT_WEIGHT = XS_NLO_PB * 1000.0 * LUMI_FB / N_GEN  # = 0.019498 per event

# MET bin edges
MET_EDGES = [250.0, 350.0, 450.0, 550.0, 650.0]
N_BINS    = len(MET_EDGES) - 1

# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def dphi(phi1, phi2):
    """Delta phi wrapped into (-pi, pi]."""
    dp = phi1 - phi2
    while dp >  math.pi: dp -= 2 * math.pi
    while dp < -math.pi: dp += 2 * math.pi
    return dp


def delta_r(eta1, phi1, eta2, phi2):
    return math.sqrt((eta1 - eta2)**2 + dphi(phi1, phi2)**2)


def transverse_mass(pt_lep, phi_lep, met, phi_met):
    return math.sqrt(2.0 * pt_lep * met * (1.0 - math.cos(dphi(phi_lep, phi_met))))


# ---------------------------------------------------------------------------
# YAML update
# ---------------------------------------------------------------------------

def update_yaml(results_file, yields):
    """Write yields into the dependent_variables of the YAML results file."""
    with open(results_file) as fh:
        raw = fh.read()

    parts = raw.split("\n---\n", 1)
    if len(parts) == 2:
        meta_block, data_block = parts
    else:
        meta_block = ""
        data_block = parts[0]

    import yaml
    hist_data = yaml.safe_load(data_block)
    vals = hist_data["dependent_variables"][0]["values"]
    for i, y in enumerate(yields):
        vals[i] = {"value": round(float(y), 4)}

    out_data = yaml.dump(hist_data, default_flow_style=False, sort_keys=False)
    with open(results_file, "w") as fh:
        if meta_block:
            fh.write(meta_block + "\n---\n")
        fh.write(out_data)

    print(f"Updated {results_file}")


# ---------------------------------------------------------------------------
# Main analysis loop using PyROOT + Delphes library
# ---------------------------------------------------------------------------

def run_analysis(delphes_file):
    # Need to load Delphes library from its build directory so ROOT can resolve
    # the custom Delphes classes (Jet, MissingET, Electron, Muon, Track, etc.)
    orig_dir = os.getcwd()
    os.chdir(DELPHES_DIR)
    os.environ["ROOT_INCLUDE_PATH"] = DELPHES_DIR

    import ROOT
    ROOT.gROOT.SetBatch(True)
    ROOT.gSystem.Load("./libDelphes.so")

    os.chdir(orig_dir)

    print(f"Reading: {delphes_file}")
    root_file = ROOT.TFile(delphes_file)
    tree = root_file.Get("Delphes")
    n_ev = tree.GetEntries()
    print(f"Events in tree: {n_ev}")

    raw_counts = np.zeros(N_BINS, dtype=float)

    # Cut-flow counters
    cf = {k: 0 for k in [
        "total", "met250", "1lep", "2jets", "1btag", "mt150",
        "mindphi05", "nj5", "j1_nobtagged", "dphi_metlep2",
        "lep_pt150", "track_veto"
    ]}

    for iev in range(n_ev):
        tree.GetEntry(iev)
        cf["total"] += 1

        # ----- MET -----
        if tree.MissingET.GetEntries() == 0:
            continue
        met_obj = tree.MissingET.At(0)
        met     = met_obj.MET
        met_phi = met_obj.Phi

        if met <= 250.0:
            continue
        cf["met250"] += 1

        # ----- Electrons (pT>20, |eta|<2.1) -----
        electrons = []
        for i in range(tree.Electron.GetEntries()):
            e = tree.Electron.At(i)
            if e.PT > 20.0 and abs(e.Eta) < 2.1:
                electrons.append((e.PT, e.Eta, e.Phi, "e"))

        # ----- Muons (pT>20, |eta|<2.4) -----
        muons = []
        for i in range(tree.Muon.GetEntries()):
            m = tree.Muon.At(i)
            if m.PT > 20.0 and abs(m.Eta) < 2.4:
                muons.append((m.PT, m.Eta, m.Phi, "mu"))

        leptons = electrons + muons

        # Exactly 1 lepton
        if len(leptons) != 1:
            continue
        cf["1lep"] += 1

        lep_pt, lep_eta, lep_phi, _ = leptons[0]

        # ----- Jets (pT>30, |eta|<2.4, DR>0.4 from lepton) -----
        jets = []
        for i in range(tree.Jet.GetEntries()):
            j = tree.Jet.At(i)
            if j.PT <= 30.0 or abs(j.Eta) >= 2.4:
                continue
            if delta_r(j.Eta, j.Phi, lep_eta, lep_phi) < 0.4:
                continue
            btag = int(j.BTag & 1)   # bit 0 = medium b-tag WP in Delphes CMS card
            jets.append((j.PT, j.Eta, j.Phi, btag))

        # Sort descending by pT
        jets.sort(key=lambda x: -x[0])

        if len(jets) < 2:
            continue
        cf["2jets"] += 1

        # At least 1 b-tagged jet
        n_btag = sum(1 for jt in jets if jt[3] == 1)
        if n_btag < 1:
            continue
        cf["1btag"] += 1

        # Transverse mass
        mt = transverse_mass(lep_pt, lep_phi, met, met_phi)
        if mt <= 150.0:
            continue
        cf["mt150"] += 1

        # min_dphi(MET, J1orJ2) > 0.5 (relaxed from 0.8 for compressed)
        dphi_j1 = abs(dphi(met_phi, jets[0][2]))
        dphi_j2 = abs(dphi(met_phi, jets[1][2]))
        if min(dphi_j1, dphi_j2) <= 0.5:
            continue
        cf["mindphi05"] += 1

        # ----- Compressed-specific cuts -----

        # NJ >= 5
        if len(jets) < 5:
            continue
        cf["nj5"] += 1

        # Leading jet NOT b-tagged
        if jets[0][3] == 1:
            continue
        cf["j1_nobtagged"] += 1

        # dphi(MET, lepton) < 2
        if abs(dphi(met_phi, lep_phi)) >= 2.0:
            continue
        cf["dphi_metlep2"] += 1

        # pT(lepton) < 150 GeV
        if lep_pt >= 150.0:
            continue
        cf["lep_pt150"] += 1

        # ----- Lepton veto: no extra leptons pT>5 GeV -----
        # (already enforced by exactly-1-lepton, but check pT>5 objects too)
        extra_lep = False
        for i in range(tree.Electron.GetEntries()):
            e = tree.Electron.At(i)
            if e.PT > 5.0 and abs(e.Eta) < 2.5 and delta_r(e.Eta, e.Phi, lep_eta, lep_phi) > 0.1:
                extra_lep = True
                break
        if not extra_lep:
            for i in range(tree.Muon.GetEntries()):
                m = tree.Muon.At(i)
                if m.PT > 5.0 and abs(m.Eta) < 2.4 and delta_r(m.Eta, m.Phi, lep_eta, lep_phi) > 0.1:
                    extra_lep = True
                    break
        if extra_lep:
            continue

        # ----- Track veto -----
        # Veto if any track (pT>10, |eta|<2.4) is:
        #   - not matching the lepton (DR > 0.3)
        #   - isolated from all selected jets (DR > 0.4 from every jet)
        has_iso_track = False
        for i in range(tree.Track.GetEntries()):
            trk = tree.Track.At(i)
            if trk.PT <= 10.0 or abs(trk.Eta) >= 2.4:
                continue
            if delta_r(trk.Eta, trk.Phi, lep_eta, lep_phi) <= 0.3:
                continue
            # Check isolation from selected jets
            isolated = True
            for jt in jets:
                if delta_r(trk.Eta, trk.Phi, jt[1], jt[2]) <= 0.4:
                    isolated = False
                    break
            if isolated:
                has_iso_track = True
                break
        if has_iso_track:
            continue
        cf["track_veto"] += 1

        # ----- Fill MET histogram -----
        # Last bin is overflow-inclusive: MET >= 550 GeV all go in bin 3.
        if met >= MET_EDGES[N_BINS - 1]:
            raw_counts[N_BINS - 1] += 1
        else:
            for ibin in range(N_BINS - 1):
                if MET_EDGES[ibin] <= met < MET_EDGES[ibin + 1]:
                    raw_counts[ibin] += 1
                    break

        if iev % 5000 == 0:
            print(f"  Processed {iev}/{n_ev} events...", flush=True)

    root_file.Close()

    yields = raw_counts * EVT_WEIGHT

    print("\n--- Cut flow ---")
    for step, count in cf.items():
        print(f"  {step:20s}  {count:6d}")

    print("\n--- MET histogram ---")
    for ibin in range(N_BINS):
        lo, hi = MET_EDGES[ibin], MET_EDGES[ibin + 1]
        print(f"  [{lo:.0f},{hi:.0f}] GeV:  {raw_counts[ibin]:.0f} raw  ->  {yields[ibin]:.4f} expected events")

    return raw_counts, yields


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(DELPHES_FILE):
        print(f"ERROR: Delphes file not found: {DELPHES_FILE}")
        sys.exit(1)

    raw_counts, yields = run_analysis(DELPHES_FILE)
    update_yaml(RESULTS_FILE, yields)
    print("\nDone.")


if __name__ == "__main__":
    main()
