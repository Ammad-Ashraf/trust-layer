#!/usr/bin/env python3
"""Entry point for bin/run-analysis. CMS-SUS-16-046 T5Wg signal region analysis."""
import uproot  # noqa: F401 — imported here so pre-flight detects it
import yaml
import sys
import os

# Read data file path from datasets.yaml
with open("datasets.yaml") as _f:
    _datasets = yaml.safe_load(_f) or []
_mc = next((d for d in _datasets if d.get("process") == "T5Wg_1750_1700"), None)
if _mc is None or not _mc.get("file_urls"):
    print("ERROR: T5Wg_1750_1700 not found in datasets.yaml", file=sys.stderr)
    sys.exit(1)

# Inject the resolved path so analysis/analysis.py can pick it up
os.environ["ANALYSIS_DATA_FILE"] = _mc["file_urls"][0]

import runpy
runpy.run_path("analysis/analysis.py", run_name="__main__")
