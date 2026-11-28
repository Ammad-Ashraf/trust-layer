#!/usr/bin/env python3
"""
CMS-SUS-16-046: T5Wg analysis for binned S_T^gamma differential yield.

Event selection implements Table 1 from CMS-SUS-16-046, with signal region defined by:
- At least one photon with pT > 180 GeV in |eta| < 1.44
- p_miss_T > 300 GeV
- M_T(gamma, p_miss_T) > 300 GeV
- S_T^gamma in bins: 600-800, 800-1000, 1000-1300, >1300 GeV

Output: Fill results/histogram_T5Wg.yaml with signal yields normalized to 35.9 fb^-1
"""

import sys
import os
import numpy as np
import uproot
import awkward as ak
import yaml
from pathlib import Path

# Signal region S_T^gamma bin edges (GeV)
STGAMMA_BINS = [600.0, 800.0, 1000.0, 1300.0, 1600.0]
LUMINOSITY_FB = 35.9

def delta_phi(phi1, phi2):
    """Compute delta phi between two angles."""
    dphi = np.abs(phi1 - phi2)
    return np.minimum(dphi, 2*np.pi - dphi)

def delta_r(eta1, phi1, eta2, phi2):
    """Compute delta R between two objects."""
    deta = eta1 - eta2
    dphi = delta_phi(phi1, phi2)
    return np.sqrt(deta**2 + dphi**2)

def transverse_mass(pt_lep, phi_lep, pt_met, phi_met):
    """Compute transverse mass between object and MET."""
    dphi = delta_phi(phi_lep, phi_met)
    return np.sqrt(2 * pt_lep * pt_met * (1 - np.cos(dphi)))

class T5WgAnalysis:
    """CMS-SUS-16-046 T5Wg event selection and histogram."""

    def __init__(self):
        self.events = {}
        self.hist = np.zeros(len(STGAMMA_BINS) - 1)
        self.total_events = 0
        self.selected_events = 0

    def load_root_files(self, data_dir='data'):
        """Load all Delphes ROOT files from data directory."""
        root_files = sorted(Path(data_dir).glob('*.root'))

        if not root_files:
            print(f"Warning: No ROOT files found in {data_dir}/")
            return False

        print(f"Loading {len(root_files)} ROOT files...")

        all_data = {}
        for root_file in root_files:
            print(f"  Reading {root_file.name}...")
            try:
                with uproot.open(str(root_file)) as f:
                    tree = f['Delphes']

                    # Read branches
                    data = {
                        'Photon_pt': tree['Photon.PT'].array(library='ak'),
                        'Photon_eta': tree['Photon.Eta'].array(library='ak'),
                        'Photon_phi': tree['Photon.Phi'].array(library='ak'),
                        'Jet_pt': tree['Jet.PT'].array(library='ak'),
                        'Jet_eta': tree['Jet.Eta'].array(library='ak'),
                        'Jet_phi': tree['Jet.Phi'].array(library='ak'),
                    }

                    # MET reconstruction from MissingET branch
                    met_pt = tree['MissingET.MET'].array(library='ak')
                    met_phi = tree['MissingET.Phi'].array(library='ak')

                    data['MET_pt'] = met_pt
                    data['MET_phi'] = met_phi

                    # Merge with existing data
                    if not all_data:
                        all_data = data
                    else:
                        for key in data:
                            all_data[key] = ak.concatenate([all_data[key], data[key]])

            except Exception as e:
                print(f"    Error reading {root_file}: {e}")
                continue

        self.events = all_data
        self.total_events = len(all_data['Photon_pt'])
        print(f"Total events loaded: {self.total_events}")
        return self.total_events > 0

    def apply_selection(self):
        """Apply CMS-SUS-16-046 event selection from Table 1."""

        photon_pt = self.events['Photon_pt']
        photon_eta = self.events['Photon_eta']
        photon_phi = self.events['Photon_phi']
        jet_pt = self.events['Jet_pt']
        jet_eta = self.events['Jet_eta']
        jet_phi = self.events['Jet_phi']
        met_pt = self.events['MET_pt']
        met_phi = self.events['MET_phi']

        # Preselection: at least one photon with pT > 180 GeV in |eta| < 1.44 (barrel)
        good_photon = (photon_pt > 180.0) & (np.abs(photon_eta) < 1.44)
        has_good_photon = ak.sum(good_photon, axis=1) >= 1

        # Leading photon among selected photons
        photon_pt_masked = ak.where(good_photon, photon_pt, -999)
        leading_photon_idx = ak.argmax(photon_pt_masked, axis=1, keepdims=False)

        # Extract leading photon properties using fancy indexing
        events_range = np.arange(len(photon_pt))
        leading_photon_pt = photon_pt[events_range, leading_photon_idx]
        leading_photon_phi = photon_phi[events_range, leading_photon_idx]

        # Jet-MET angular separation: Dphi > 0.3 for high-pT jets
        high_pt_jets = jet_pt > 100.0
        dphi_met_jet = delta_phi(jet_phi, met_phi)

        # Check if all high-pT jets satisfy the angle cut
        good_angle = ak.all((dphi_met_jet > 0.3) | ~high_pt_jets, axis=1)

        # Transverse mass cut: MT(gamma, p_miss_T) > 300 GeV
        mt_gamma_met = transverse_mass(leading_photon_pt, leading_photon_phi, met_pt, met_phi)

        # Signal region: p_miss_T > 300 GeV and MT > 300 GeV
        signal_region = (has_good_photon &
                        good_angle &
                        (met_pt > 300.0) &
                        (mt_gamma_met > 300.0))

        print(f"Events passing preselection: {ak.sum(has_good_photon)}")
        print(f"Events with good jet angles: {ak.sum(good_angle)}")
        print(f"Events with p_miss_T > 300: {ak.sum(met_pt > 300)}")
        print(f"Events with MT > 300: {ak.sum(mt_gamma_met > 300)}")
        print(f"Events in signal region: {ak.sum(signal_region)}")

        # Compute S_T^gamma = p_miss_T + sum(pT of all photons)
        sum_photon_pt = ak.sum(photon_pt, axis=1)
        st_gamma = met_pt + sum_photon_pt

        # Apply S_T^gamma > 600 GeV cut
        final_cut = signal_region & (st_gamma > 600.0)

        st_gamma_selected = st_gamma[final_cut]
        self.selected_events = len(st_gamma_selected)

        print(f"Events passing all cuts: {self.selected_events}")
        print(f"Selection efficiency: {100*self.selected_events/self.total_events:.2f}%")

        return ak.to_numpy(st_gamma_selected)

    def fill_histogram(self, st_gamma_values):
        """Fill histogram in S_T^gamma bins."""
        self.hist, _ = np.histogram(st_gamma_values, bins=STGAMMA_BINS)

        print("\nSignal yields by S_T^gamma bin:")
        for i, (low, high) in enumerate(zip(STGAMMA_BINS[:-1], STGAMMA_BINS[1:])):
            print(f"  {low:6.0f}-{high:6.0f} GeV: {self.hist[i]:8.1f}")

    def save_results(self, output_yaml='results/histogram_T5Wg.yaml'):
        """Save histogram to YAML file matching HEPData format."""

        # Read template to preserve structure
        with open(output_yaml, 'r') as f:
            content = f.read()

        # Split metadata and histogram sections
        parts = content.split('---')
        metadata = parts[0]

        # Update histogram values
        histogram_data = {
            'dependent_variables': [
                {
                    'header': {'name': 'T5Wg_1750_1700'},
                    'values': [{'value': float(v)} for v in self.hist]
                }
            ],
            'independent_variables': [
                {
                    'header': {'name': 'STGAMMA', 'units': 'GEV'},
                    'values': [
                        {'low': float(STGAMMA_BINS[i]), 'high': float(STGAMMA_BINS[i+1])}
                        for i in range(len(STGAMMA_BINS)-1)
                    ]
                }
            ]
        }

        # Write updated file
        with open(output_yaml, 'w') as f:
            f.write(metadata)
            f.write('---\n')
            yaml.dump(histogram_data, f, default_flow_style=False, sort_keys=False)

        print(f"\nResults saved to {output_yaml}")

def main():
    """Main analysis routine."""

    analysis = T5WgAnalysis()

    # Load ROOT files
    if not analysis.load_root_files():
        print("Error: Could not load any ROOT files. Please generate events first:")
        print("  python sims/gen_events.py")
        return False

    # Apply event selection
    st_gamma_values = analysis.apply_selection()

    if len(st_gamma_values) == 0:
        print("Warning: No events passed selection!")
        analysis.hist = np.zeros(len(STGAMMA_BINS) - 1)
    else:
        analysis.fill_histogram(st_gamma_values)

    # Save results
    analysis.save_results()

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
