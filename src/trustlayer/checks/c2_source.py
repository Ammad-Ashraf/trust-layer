"""C2 Source. Guards 1b (wrong source: the generator's LO cross section instead of NLO).

Passes when sigma's `source_type` is prospino, xsec_wg or paper, its `source` text is filled in,
and, if the agent also recorded the generator's own sigma, the two differ by more than 1%
(an equal value means the LO number was used under another label).
"""

from __future__ import annotations

from trustlayer.checks.base import CheckInputs, CheckResult, result
from trustlayer.ledger.model import CROSS_SECTION, GENERATOR_CROSS_SECTION
from trustlayer.ledger.units import UnitError

ACCEPTED_SOURCES = ("prospino", "xsec_wg", "paper")
SAME_AS_GENERATOR = 0.01


def check_source(inputs: CheckInputs) -> CheckResult:
    """C2: sigma comes from Prospino NLO, the SUSY cross-section WG or the paper, not LO."""
    sigma = inputs.ledger.get(CROSS_SECTION)
    if sigma is None or sigma.value is None:
        return result("C2", "1b", [], ["skipped: no cross section recorded (see C3)"])
    problems: list[str] = []
    if sigma.source_type not in ACCEPTED_SOURCES:
        given = sigma.source_type or "none"
        problems.append(
            f"cross_section source_type is {given!r}; it must be one of "
            f"{', '.join(ACCEPTED_SOURCES)} (a generator's LO sigma is not enough)"
        )
    if not (sigma.source and sigma.source.strip()):
        problems.append("cross_section has no source text: name the tool and settings, or table")
    generator = inputs.ledger.get(GENERATOR_CROSS_SECTION)
    if generator is not None and generator.value is not None:
        try:
            ours, theirs = sigma.quantity().canonical(), generator.quantity().canonical()
        except (ValueError, UnitError):
            pass  # unit problems are C1's job
        else:
            if theirs > 0 and abs(ours / theirs - 1) <= SAME_AS_GENERATOR:
                problems.append(
                    f"cross_section ({sigma.value:g} {sigma.unit}) equals the generator's own "
                    f"sigma ({generator.value:g} {generator.unit}): that is the LO value; use "
                    "the NLO value from bin/prospino or the paper"
                )
    return result("C2", "1b", problems)
