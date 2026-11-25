"""Read the agent's own Prospino results, so C2 can verify a sigma labelled `prospino` (0017).

`bin/prospino run` writes `prospino_scratch/<process>-<hash>/prospino.dat`. That is the
agent's own visible output, so reading it obeys the fairness rule. Prospino 2.1's data row
(the header comes after it):
    [0] process  [1] i1  [2] i2  [3,4] dummy  [5] scafac  [6] m1  [7] m2  [8] angle
    [9] LO[pb]  [10] relerr  [11] NLO[pb]  [12] relerr  [13] K  [14] LO_ms[pb]  [15] NLO_ms[pb]
The free-squark-mass columns (14, 15) win when they are nonzero, as in Collider-Bench's own
parser.

`bin/prospino` runs from the Collider-Bench root, so the scratch folder there is shared by
every run on the machine. `collect` keeps only results written since this run started.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

PROCESS_CODES = frozenset(
    {"ng", "nn", "ns", "ll", "sb", "ss", "tb", "bb", "gg", "sg", "lq", "le", "hh", "ht"}
)
DAT_FILE = "prospino.dat"
SCRATCH_DIR = "prospino_scratch"


@dataclass(frozen=True)
class ProspinoResult:
    """One finished Prospino run: its process code, LO and NLO sigma in pb, and its file."""

    path: Path
    process: str
    lo_pb: float
    nlo_pb: float


def parse_dat(path: Path) -> ProspinoResult | None:
    """The result in one prospino.dat, or None if it has no complete data row."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in lines:
        cols = line.split()
        if not cols or cols[0] not in PROCESS_CODES or len(cols) < 12:
            continue
        try:
            lo, nlo = float(cols[9]), float(cols[11])
            lo_ms = float(cols[14]) if len(cols) > 14 else 0.0
            nlo_ms = float(cols[15]) if len(cols) > 15 else 0.0
        except ValueError:
            continue
        lo, nlo = (lo_ms if lo_ms > 0 else lo), (nlo_ms if nlo_ms > 0 else nlo)
        if nlo > 0:
            return ProspinoResult(path=path, process=cols[0], lo_pb=lo, nlo_pb=nlo)
    return None


def collect(scratch_roots: Iterable[Path], since: float | None) -> tuple[ProspinoResult, ...]:
    """Finished Prospino results under each `<root>/prospino_scratch/*/prospino.dat`.

    `since` is a POSIX time: older files belong to earlier runs and are skipped.
    """
    found: list[ProspinoResult] = []
    seen: set[Path] = set()
    for root in scratch_roots:
        for dat in sorted((root / SCRATCH_DIR).glob(f"*/{DAT_FILE}")):
            real = dat.resolve()
            if real in seen:
                continue
            seen.add(real)
            try:
                if since is not None and dat.stat().st_mtime < since:
                    continue
            except OSError:
                continue
            if (result := parse_dat(dat)) is not None:
                found.append(result)
    return tuple(found)
