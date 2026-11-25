"""C5 Carried through. Guards 1e (right value computed but never used in the answer).

Passes when the results file exists, every bin is filled, and the bins' sum equals the ledger's
sigma*L*BR*eps*corrections within the tolerance tau (decision 0016). It also catches an agent
that skips the ledger: with nothing recorded there is nothing to match.
"""

from __future__ import annotations

from trustlayer.checks.base import CheckInputs, CheckResult, result
from trustlayer.ledger.units import UnitError


def _how_far(total: float, expected: float) -> str:
    if total <= 0:
        return "the bins sum to zero or less"
    ratio = total / expected
    if ratio >= 1:
        return f"{ratio:.3g}x larger than the ledger"
    return f"{1 / ratio:.3g}x smaller than the ledger"


def check_carried(inputs: CheckInputs) -> CheckResult:
    """C5: the submitted bins add up to the ledger's own formula, within tau."""
    sub = inputs.submission
    if sub is None:
        reason = inputs.submission_error or "no results file found"
        return result("C5", "1e", [f"cannot read your results: {reason}"])
    empty = [str(i + 1) for i, b in enumerate(sub.bins) if b is None]
    if empty:
        return result(
            "C5", "1e", [f"{sub.path}: bin(s) {', '.join(empty)} still null; fill every bin"]
        )
    missing = inputs.ledger.missing_factors()
    where = f" in {inputs.ledger_path}" if inputs.ledger_path else ""
    if missing:
        return result(
            "C5",
            "1e",
            [
                f"cannot compare your results with the ledger{where}: {', '.join(missing)} not "
                "recorded. Record every factor you used with bin/record-quantity"
            ],
        )
    try:
        product = inputs.ledger.product()
    except (ValueError, UnitError) as exc:
        return result("C5", "1e", [f"cannot compute sigma*L*BR*eps from the ledger: {exc}"])
    if not product.unit_free or product.value <= 0:
        return result(
            "C5", "1e", ["the ledger's formula is not a positive, unit-free number (see C1)"]
        )
    total = sum(b for b in sub.bins if b is not None)
    diff = abs(total - product.value) / product.value
    if diff > inputs.c5_tolerance:
        return result(
            "C5",
            "1e",
            [
                f"your ledger{where} gives sigma*L*BR*eps = {product.value:.4g} events, "
                f"but the bins in {sub.path} sum to {total:.4g} "
                f"({_how_far(total, product.value)}; allowed difference "
                f"{inputs.c5_tolerance:.0%}). Fix whichever is wrong; record any extra "
                "factor you applied with `bin/record-quantity correction`"
            ],
        )
    return result("C5", "1e", [], [f"bins sum to {total:.4g}, ledger gives {product.value:.4g}"])
