"""Download the papers in papers/papers.yaml into papers/pdf/ (git-ignored).

Usage:
    python scripts/fetch_papers.py              # all papers with an arXiv id
    python scripts/fetch_papers.py --priority core
    python scripts/fetch_papers.py --text       # also extract .txt (needs the [papers] extra)

Skips files that already exist. PDFs are data: never executed, never committed.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "papers" / "papers.yaml"
OUT = ROOT / "papers" / "pdf"
USER_AGENT = "trustlayer-paper-fetch/0.1"


def download(arxiv_id: str, dest: Path) -> None:
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"{arxiv_id}: response is not a PDF")
    dest.write_bytes(data)


def extract_text(pdf: Path) -> None:
    from pypdf import PdfReader

    logging.getLogger("pypdf").setLevel(logging.ERROR)  # font warnings are noise here
    text = "\n\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
    pdf.with_suffix(".txt").write_text(text, encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--priority", choices=["core", "related", "background"])
    parser.add_argument("--text", action="store_true", help="also extract plain text")
    args = parser.parse_args()

    papers = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["papers"]
    OUT.mkdir(parents=True, exist_ok=True)
    failures = 0
    for paper in papers:
        if not paper.get("arxiv") or (args.priority and paper["priority"] != args.priority):
            continue
        dest = OUT / f"{paper['id']}.pdf"
        try:
            if not dest.exists():
                download(paper["arxiv"], dest)
                print(f"downloaded {dest.name}")
                time.sleep(3)  # be polite to arXiv
            if args.text and not dest.with_suffix(".txt").exists():
                extract_text(dest)
        except Exception as error:  # report and continue with the rest
            failures += 1
            print(f"FAILED {paper['id']}: {error}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
