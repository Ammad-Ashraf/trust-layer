#!/usr/bin/env python3
"""
CMS-SUS-16-046: Search for GMSB SUSY in photon + MET final states.
Main analysis script - reads Delphes ROOT files and fills histogram.
"""

import sys
import math
import yaml
from pathlib import Path

try:
    import uproot
    import numpy as np
except ImportError as e:
    print(f"Error: Required package missing: {e}", file=sys.stderr)
    sys.exit(1)


def analyze_events(input_file):
    """
    Read Delphes ROOT file and apply CMS-SUS-16-046 event selection.
    Returns S_T^gamma values for selected events in signal region.
    """

    print(f"Processing {input_file}...")

    try:
        with uproot.open(input_file) as f:
            tree = f["Delphes"]
            n_events = tree.num_entries

            # Read branches - safe access
            photon_pt = tree["Photon/Photon.PT"].array(library="np")
            photon_eta = tree["Photon/Photon.Eta"].array(library="np")
            photon_phi = tree["Photon/Photon.Phi"].array(library="np")
            met_pt = tree["MissingET/MissingET.MET"].array(library="np")
            met_phi = tree["MissingET/MissingET.Phi"].array(library="np")
            jet_pt = tree["Jet/Jet.PT"].array(library="np")
            jet_eta = tree["Jet/Jet.Eta"].array(library="np")
            jet_phi = tree["Jet/Jet.Phi"].array(library="np")
    except Exception as e:
        print(f"Error reading ROOT file {input_file}: {e}")
        return np.array([])

    print(f"  Total events: {n_events}")

    # Event selection cuts from CMS-SUS-16-046

    # Preselection: at least one photon with pT > 180 GeV in barrel |η| < 1.44
    has_good_photon = np.zeros(n_events, dtype=bool)
    for i in range(n_events):
        for j in range(len(photon_pt[i])):
            if photon_pt[i][j] > 180 and abs(photon_eta[i][j]) < 1.44:
                has_good_photon[i] = True
                break

    n_presel = np.sum(has_good_photon)
    print(f"  After photon preselection: {n_presel}")

    if n_presel == 0:
        return np.array([])

    # Photon isolation: DR(γ, jet) > 0.5
    isolated = np.ones(n_events, dtype=bool)
    for i in range(n_events):
        if not has_good_photon[i]:
            isolated[i] = False
            continue

        # For each photon in this event, check isolation
        is_isolated_event = True
        for j in range(len(photon_pt[i])):
            p_eta, p_phi = photon_eta[i][j], photon_phi[i][j]

            # Check deltaR to all jets
            min_dr = float('inf')
            for k in range(len(jet_pt[i])):
                deta = p_eta - jet_eta[i][k]
                dphi = p_phi - jet_phi[i][k]
                # Normalize phi difference
                dphi = math.atan2(math.sin(dphi), math.cos(dphi))
                dr = math.sqrt(deta**2 + dphi**2)
                min_dr = min(min_dr, dr)

            if min_dr <= 0.5:
                is_isolated_event = False
                break

        isolated[i] = is_isolated_event

    n_isolated = np.sum(isolated)
    print(f"  After photon isolation: {n_isolated}")

    # Jet-MET angle: |Δφ(pT_miss, jet)| > 0.3 for pT(jet) > 100 GeV
    good_met_angle = np.ones(n_events, dtype=bool)
    for i in range(n_events):
        if not isolated[i]:
            good_met_angle[i] = False
            continue

        good_angle_event = True
        for j in range(len(jet_pt[i])):
            if jet_pt[i][j] > 100:
                dphi = jet_phi[i][j] - met_phi[i]
                dphi = math.atan2(math.sin(dphi), math.cos(dphi))
                if abs(dphi) <= 0.3:
                    good_angle_event = False
                    break

        good_met_angle[i] = good_angle_event

    n_good_angle = np.sum(good_met_angle)
    print(f"  After MET-jet angle cut: {n_good_angle}")

    # Signal region cuts
    # pT_miss > 300 GeV
    has_met = met_pt > 300

    # MT(γ, pT_miss) > 300 GeV, where γ is the leading pT photon
    has_mt = np.ones(n_events, dtype=bool)
    for i in range(n_events):
        if not (good_met_angle[i] and has_met[i]):
            has_mt[i] = False
            continue

        # Find highest pT photon
        if len(photon_pt[i]) == 0:
            has_mt[i] = False
            continue

        max_pt_idx = np.argmax(photon_pt[i])
        pt_max = photon_pt[i][max_pt_idx]
        eta_max = photon_eta[i][max_pt_idx]
        phi_max = photon_phi[i][max_pt_idx]

        dphi = phi_max - met_phi[i]
        dphi = math.atan2(math.sin(dphi), math.cos(dphi))
        mt = math.sqrt(2 * pt_max * met_pt[i] * (1 - math.cos(dphi)))

        has_mt[i] = mt > 300

    n_has_mt = np.sum(has_mt)
    print(f"  After MT cut: {n_has_mt}")

    # Combine all signal region cuts
    signal_region = good_met_angle & has_met & has_mt
    n_signal = np.sum(signal_region)
    print(f"  Events in signal region: {n_signal}")

    if n_signal == 0:
        return np.array([])

    # Compute S_T^gamma = pT_miss + sum(pT_gamma)
    st_gamma_values = []
    for i in range(n_events):
        if signal_region[i]:
            photon_sum = np.sum(photon_pt[i]) if len(photon_pt[i]) > 0 else 0
            st_gamma = met_pt[i] + photon_sum
            st_gamma_values.append(st_gamma)

    return np.array(st_gamma_values)


def fill_histogram(st_gamma_values):
    """
    Fill histogram bins for S_T^gamma.
    Bins: 600-800, 800-1000, 1000-1300, >1300 GeV
    """

    if len(st_gamma_values) == 0:
        return [0, 0, 0, 0]

    bins = [600, 800, 1000, 1300, float('inf')]
    counts = []

    for i in range(len(bins) - 1):
        count = np.sum((st_gamma_values >= bins[i]) & (st_gamma_values < bins[i+1]))
        counts.append(int(count))

    return counts


def main():
    # Find all ROOT files in data directory
    data_dir = Path("data")
    root_files = sorted(data_dir.glob("*.root"))

    if not root_files:
        print("Error: No ROOT files found in data/")
        return False

    print(f"Found {len(root_files)} ROOT file(s)")

    # Analyze all files
    all_st_gamma = []
    for root_file in root_files:
        st_gamma = analyze_events(str(root_file))
        all_st_gamma.extend(st_gamma)

    all_st_gamma = np.array(all_st_gamma)

    print(f"\nTotal events in signal region: {len(all_st_gamma)}")

    # Fill histogram
    bin_counts = fill_histogram(all_st_gamma)

    print("\nHistogram bin counts:")
    bin_names = ["600-800 GeV", "800-1000 GeV", "1000-1300 GeV", ">1300 GeV"]
    for name, count in zip(bin_names, bin_counts):
        print(f"  {name}: {count}")

    # Update YAML results file
    results_file = Path("results/histogram_T5Wg.yaml")
    if results_file.exists():
        with open(results_file, 'r') as f:
            content = f.read()

        # Split into two YAML documents
        parts = content.split('---')
        if len(parts) == 2:
            metadata_str, histogram_str = parts[0].strip(), parts[1].strip()

            # Parse histogram
            histogram = yaml.safe_load(histogram_str)

            # Update bin values
            if 'dependent_variables' in histogram and len(histogram['dependent_variables']) > 0:
                for i, count in enumerate(bin_counts):
                    histogram['dependent_variables'][0]['values'][i] = {'value': count}

            # Write updated YAML
            metadata = yaml.safe_load(metadata_str)
            with open(results_file, 'w') as f:
                yaml.dump(metadata, f, default_flow_style=False)
                f.write("---\n")
                yaml.dump(histogram, f, default_flow_style=False)

            print(f"\nUpdated {results_file}")
        else:
            print(f"Warning: Could not parse YAML file {results_file}")
    else:
        print(f"Warning: Results file not found at {results_file}")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
