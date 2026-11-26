"""
Entry point for bin/run-analysis.
Runs the CMS-SUS-16-034 VZ electroweak selection on the
TChiWZ_550_200 HepMC3 sample and writes results to
results/histogram_TChiWZ.yaml.

Signal MC sample catalog: datasets.yaml
"""
import sys
import os

# Allow importing from analysis/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analysis'))

from analysis_TChiWZ import analyze, fill_yaml

ws_dir = os.path.dirname(os.path.abspath(__file__))
hepmc_file = os.path.join(ws_dir, 'sims', 'TChiWZ_550_200.hepmc')
yaml_path = os.path.join(ws_dir, 'results', 'histogram_TChiWZ.yaml')

counts = analyze(hepmc_file)
fill_yaml(counts, yaml_path)
