"""
CMS-SUS-16-051 compressed signal region analysis — workspace root entry point.
Reads datasets.yaml, runs the selection on each ROOT file, fills histogram_T2tt_comp.yaml.
"""
import os
import sys
import importlib.util
import yaml
import numpy as np
import uproot  # noqa: F401 — required by pre-flight check

WORKSPACE = os.path.dirname(os.path.abspath(__file__))

# Load analysis/analysis.py by path to avoid shadowing by this file
_spec = importlib.util.spec_from_file_location(
    "_analysis_impl",
    os.path.join(WORKSPACE, "analysis", "analysis.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
run_analysis = _mod.run_analysis
normalize_and_write = _mod.normalize_and_write
write_yaml = _mod.write_yaml

def main():
    datasets_path = os.path.join(WORKSPACE, "datasets.yaml")
    with open(datasets_path) as f:
        datasets = yaml.safe_load(f) or []

    all_counts = np.zeros(4)
    n_gen_total = 0
    xsec_pb = None

    for ds in datasets:
        status = ds.get("status", "")
        if status.startswith("BLOCKED"):
            continue
        xsec_pb = ds.get("cross_section_pb", 0.0272)
        for url in ds.get("file_urls", []):
            root_file = url if os.path.isabs(url) else os.path.join(WORKSPACE, url)
            counts, n = run_analysis(root_file)
            all_counts += counts
            n_gen_total += n

    if n_gen_total == 0:
        print("ERROR: no events processed", file=sys.stderr)
        sys.exit(1)

    lumi_fb = 35.9
    expected = normalize_and_write(all_counts, n_gen_total, xsec_pb, lumi_fb)

    yaml_path = os.path.join(WORKSPACE, "results", "histogram_T2tt_comp.yaml")
    write_yaml(expected, yaml_path)

    print(f"\nFinal yields (normalized to {lumi_fb} fb^-1):")
    bin_edges = [(250,350),(350,450),(450,550),(550,650)]
    for (lo,hi), val in zip(bin_edges, expected):
        print(f"  MET [{lo},{hi}] GeV: {val:.4f}")
    print(f"  Total: {sum(expected):.4f}")

if __name__ == "__main__":
    main()
