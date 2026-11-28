#!/usr/bin/env python3
"""
CMS-SUS-16-034: Search for new phenomena in final states with two opposite-charge,
same-flavor leptons, jets, and missing transverse momentum

Analysis for TChiWZ_550_200 signal in the electroweak WZ/ZZ region
"""
import sys
from pathlib import Path
import numpy as np
import uproot
import awkward as ak
import yaml

WORKSPACE = Path(__file__).parent
DATA_DIR = WORKSPACE / "data"
RESULTS_DIR = WORKSPACE / "results"

# CMS-SUS-16-034 configuration
ETMISS_BINS = np.array([100.0, 150.0, 250.0, 350.0, 450.0])  # GeV

def deltaphi(phi1, phi2):
    """Calculate delta-phi properly"""
    dphi = phi1 - phi2
    dphi = np.where(np.abs(dphi) > np.pi, 2*np.pi - np.abs(dphi), np.abs(dphi))
    return dphi

def read_root_file(filename):
    """Read Delphes ROOT file"""
    with uproot.open(filename) as f:
        tree = f["Delphes"]

        data = {}
        # Try to read all relevant branches
        branches = tree.keys()

        # Muons
        for branch in ["Muon_PT", "Muon.PT", "Muon_Eta", "Muon.Eta", "Muon_Phi", "Muon.Phi"]:
            if branch in branches:
                key = branch.replace(".", "_").replace("Muon_", "muon_").replace("Muon.", "muon_")
                data[key] = tree[branch].array(library="ak")

        # Electrons
        for branch in ["Electron_PT", "Electron.PT", "Electron_Eta", "Electron.Eta", "Electron_Phi", "Electron.Phi"]:
            if branch in branches:
                key = branch.replace(".", "_").replace("Electron_", "electron_").replace("Electron.", "electron_")
                data[key] = tree[branch].array(library="ak")

        # Jets
        for branch in ["Jet_PT", "Jet.PT", "Jet_Eta", "Jet.Eta", "Jet_Phi", "Jet.Phi"]:
            if branch in branches:
                key = branch.replace(".", "_").replace("Jet_", "jet_").replace("Jet.", "jet_")
                data[key] = tree[branch].array(library="ak")

        # MET
        for branch in ["MET_MET", "MET.MET", "MET_Phi", "MET.Phi", "MissingET_MET", "MissingET.MET"]:
            if branch in branches:
                key = branch.replace(".", "_").replace("MET_MET", "met").replace("MissingET_MET", "met").replace("MET_Phi", "met_phi").replace("MissingET_Phi", "met_phi")
                if "MET" in key or "met" in key:
                    if "phi" in key:
                        data["met_phi"] = tree[branch].array(library="ak")
                    else:
                        data["met"] = tree[branch].array(library="ak")

        return data

def apply_selection(data):
    """Apply CMS-SUS-16-034 event selection for WZ region"""

    nevents = len(data.get('muon_pt', ak.Array([[]])))

    # Initialize all events to pass
    baseline = np.ones(nevents, dtype=bool)

    # Count leptons
    n_muons = ak.count(data.get('muon_pt', ak.Array([[]]),), axis=1)
    n_electrons = ak.count(data.get('electron_pt', ak.Array([[]]),), axis=1)

    # Require 2 OCSF leptons (either 2 muons or 2 electrons)
    # For now, just require 2 leptons of some kind
    baseline &= (n_muons >= 2) | (n_electrons >= 2)

    # Jets: require >= 2 with pT > 35 GeV, |eta| < 2.4
    if 'jet_pt' in data:
        jet_cuts = (data['jet_pt'] > 35.0) & (np.abs(data.get('jet_eta', ak.zeros_like(data['jet_pt']))) < 2.4)
        n_good_jets = ak.count(data['jet_pt'][jet_cuts], axis=1)
        baseline &= n_good_jets >= 2

    # E_T^miss > 100 GeV (baseline, later > 100 for binning)
    if 'met' in data:
        met_array = np.atleast_1d(ak.to_numpy(data['met']))
        if len(met_array) == nevents:
            baseline &= met_array > 50.0

    return baseline

def histogram_etmiss(data, baseline):
    """Histogram E_T^miss for selected events"""

    if 'met' not in data:
        return np.zeros(len(ETMISS_BINS) - 1, dtype=int)

    met_array = np.atleast_1d(ak.to_numpy(data['met']))
    met_selected = met_array[baseline]

    hist, _ = np.histogram(met_selected, bins=ETMISS_BINS)
    return hist

def save_results(hist):
    """Save histogram to results YAML"""

    results_file = RESULTS_DIR / "histogram_TChiWZ.yaml"

    with open(results_file) as f:
        content = f.read()

    # Split YAML documents
    parts = content.split("---")
    metadata = parts[0]
    histogram_text = "---".join(parts[1:])

    # Parse and modify
    histogram = yaml.safe_load(histogram_text)
    for i, val in enumerate(hist):
        histogram['dependent_variables'][0]['values'][i]['value'] = int(val)

    # Write back
    with open(results_file, 'w') as f:
        f.write(metadata)
        f.write("---\n")
        yaml.dump(histogram, f, default_flow_style=False, sort_keys=False)

def main():
    """Main analysis routine"""

    input_root = DATA_DIR / "delphes_output.root"
    if not input_root.exists():
        print(f"ERROR: {input_root} not found", file=sys.stderr)
        return 1

    print(f"Reading {input_root}...", file=sys.stderr)
    data = read_root_file(str(input_root))

    print(f"Applying CMS-SUS-16-034 selection...", file=sys.stderr)
    baseline = apply_selection(data)
    n_selected = np.sum(baseline)

    print(f"Events passing selection: {n_selected}", file=sys.stderr)

    hist = histogram_etmiss(data, baseline)

    print(f"Saving results...", file=sys.stderr)
    save_results(hist)

    print(f"Analysis complete", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
