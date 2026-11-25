"""C2 Source. Guards 1b (wrong source: the generator's LO cross section instead of NLO).

Passes when sigma's `source_type` is prospino, xsec_wg or paper, and its `source` text is
filled in. If the agent also recorded the generator's own sigma, the two must differ by more
than 1%: an equal value means the LO number was used under another label.

Decision 0017: a sigma labelled `prospino` must also match (within 1%) the NLO value of a
Prospino run actually found in this run's scratch folders. A matching LO value instead is
flagged as LO. With no Prospino output at all, the label is unsupported. This is checked
whenever the gate collected the run's Prospino results (`prospino_results` is not None).
"""

from __future__ import annotations

from trustlayer.checks.base import CheckInputs, CheckResult, result
from trustlayer.checks.prospino import ProspinoResult
from trustlayer.ledger.model import CROSS_SECTION, GENERATOR_CROSS_SECTION, Entry
from trustlayer.ledger.units import UnitError

ACCEPTED_SOURCES = ("prospino", "xsec_wg", "paper")
SAME_AS_GENERATOR = 0.01
PROSPINO_MATCH = 0.01  # relative agreement between the ledger's sigma and Prospino's output


def _close(a: float, b: float, tol: float) -> bool:
    return b > 0 and abs(a / b - 1) <= tol


def _prospino_problem(
    sigma_fb: float, sigma: Entry, runs: tuple[ProspinoResult, ...]
) -> str | None:
    shown = f"{sigma.value:g} {sigma.unit}"
    if not runs:
        return (
            f"cross_section ({shown}) is labelled prospino, but this run has no finished "
            "Prospino result. Run bin/prospino and record its NLO value, or record the "
            "source you actually used"
        )
    if any(_close(sigma_fb, r.nlo_pb * 1000, PROSPINO_MATCH) for r in runs):
        return None
    if any(_close(sigma_fb, r.lo_pb * 1000, PROSPINO_MATCH) for r in runs):
        return f"cross_section ({shown}) equals a Prospino LO value; record the NLO value"
    found = ", ".join(f"{r.nlo_pb * 1000:.4g} fb ({r.process}, {r.path.parent.name})" for r in runs)
    return (
        f"cross_section ({shown}) is labelled prospino, but it matches none of this run's "
        f"Prospino NLO results: {found}"
    )


def check_source(inputs: CheckInputs) -> CheckResult:
    """C2: sigma comes from Prospino NLO, the SUSY cross-section WG or the paper, not LO."""
    sigma = inputs.ledger.get(CROSS_SECTION)
    if sigma is None or sigma.value is None:
        return result("C2", "1b", [], ["skipped: no cross section recorded (see C3)"])
    problems: list[str] = []
    notes: list[str] = []
    if sigma.source_type not in ACCEPTED_SOURCES:
        given = sigma.source_type or "none"
        problems.append(
            f"cross_section source_type is {given!r}; it must be one of "
            f"{', '.join(ACCEPTED_SOURCES)} (a generator's LO sigma is not enough)"
        )
    if not (sigma.source and sigma.source.strip()):
        problems.append("cross_section has no source text: name the tool and settings, or table")
    try:
        sigma_fb: float | None = sigma.quantity().canonical()
    except (ValueError, UnitError):
        sigma_fb = None  # unit problems are C1's job
    generator = inputs.ledger.get(GENERATOR_CROSS_SECTION)
    if sigma_fb is not None and generator is not None and generator.value is not None:
        try:
            theirs = generator.quantity().canonical()
        except (ValueError, UnitError):
            theirs = 0.0
        if _close(sigma_fb, theirs, SAME_AS_GENERATOR):
            problems.append(
                f"cross_section ({sigma.value:g} {sigma.unit}) equals the generator's own "
                f"sigma ({generator.value:g} {generator.unit}): that is the LO value; use "
                "the NLO value from bin/prospino or the paper"
            )
    if sigma.source_type == "prospino" and sigma_fb is not None:
        if inputs.prospino_results is None:
            notes.append("prospino label not verified (no run folder to look in)")
        elif (problem := _prospino_problem(sigma_fb, sigma, inputs.prospino_results)) is not None:
            problems.append(problem)
        else:
            notes.append("matches a Prospino NLO result from this run")
    return result("C2", "1b", problems, notes)
