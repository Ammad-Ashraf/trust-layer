"""`record-quantity`: the CLI the test-subject agent calls to write the ledger.

Each call records one number with its unit and source in `ledger.yaml` (the working directory
by default; `--ledger` or `$TRUSTLAYER_LEDGER` override it). Bad input is refused with a
one-line reason, so mistakes surface at the moment of entry. The checks (C1-C5) still re-run
everything when the agent tries to stop. `record-quantity show` prints the ledger and the
agent's own formula product, never any reference value.

Examples:
    record-quantity cross_section --value 3.96 --unit fb --source "bin/prospino gg NLO" \
        --source-type prospino --process gluino_pair --mass gluino=1750
    record-quantity luminosity --value 35.9 --unit fb^-1 --source "paper abstract"
    record-quantity branching_fraction --value 1 --reason "decays simulated" --source "SLHA"
    record-quantity efficiency --value 0.0093 --n-pass 93 --n-gen 10000 --source analysis.py
    record-quantity correction --name trigger --value 0.943 --source "paper Sec. 4"
    record-quantity show
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from trustlayer.ledger.io import load_ledger, save_ledger
from trustlayer.ledger.model import (
    BRANCHING_FRACTION,
    CROSS_SECTION,
    EFFICIENCY,
    GENERATOR_CROSS_SECTION,
    LUMINOSITY,
    QUANTITY_NAMES,
    SCHEMA_VERSION,
    SOURCE_TYPES,
    Entry,
    Ledger,
    LedgerError,
    empty_ledger,
)
from trustlayer.ledger.names import PARTICLES, PROCESSES, canonical_particle, canonical_process
from trustlayer.ledger.units import UnitError, parse_unit

CORRECTION = "correction"
SHOW = "show"
DEFAULT_LEDGER = "ledger.yaml"
EPS_MATCH = 0.01  # relative agreement required between efficiency and n_pass / n_gen

_EXPECTED_AREA_POWER = {
    CROSS_SECTION: 1,
    GENERATOR_CROSS_SECTION: 1,
    LUMINOSITY: -1,
    BRANCHING_FRACTION: 0,
    EFFICIENCY: 0,
    CORRECTION: 0,
}
_UNIT_HINT = {1: "fb or pb", -1: "fb^-1 or pb^-1", 0: "dimensionless"}
_NEEDS_SOURCE_TYPE = (CROSS_SECTION, GENERATOR_CROSS_SECTION)


class InputError(ValueError):
    """Bad input from the agent; the message is printed as-is."""


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="record-quantity",
        description="Record one normalization factor (with unit and source) in the ledger.",
    )
    p.add_argument("name", choices=[*QUANTITY_NAMES, CORRECTION, SHOW])
    p.add_argument("--value", type=float, help="the number")
    p.add_argument("--unit", help="fb, pb, fb^-1, pb^-1 or dimensionless")
    p.add_argument("--source", help="where the number comes from (tool + settings, table, page)")
    p.add_argument("--source-type", choices=sorted(SOURCE_TYPES))
    p.add_argument("--process", help=f"for sigma, one of: {', '.join(PROCESSES)}")
    p.add_argument(
        "--mass",
        action="append",
        default=[],
        metavar="PARTICLE=GEV",
        help=f"for sigma, repeatable; particles: {', '.join(PARTICLES)}",
    )
    p.add_argument("--reason", help="required when a branching fraction or efficiency is 1")
    p.add_argument("--n-pass", type=float, help="events passing (efficiency only)")
    p.add_argument("--n-gen", type=float, help="events generated (efficiency only)")
    p.add_argument("--uncertainty", type=float, help="absolute, same unit as the value")
    p.add_argument("--name", dest="label", help="label of a correction, e.g. trigger")
    p.add_argument(
        "--ledger", help=f"ledger file (default $TRUSTLAYER_LEDGER or ./{DEFAULT_LEDGER})"
    )
    return p


def _ledger_path(arg: str | None) -> Path:
    return Path(arg or os.environ.get("TRUSTLAYER_LEDGER") or DEFAULT_LEDGER).resolve()


def _parse_masses(items: Sequence[str]) -> dict[str, float]:
    masses: dict[str, float] = {}
    for item in items:
        particle, sep, mass = item.partition("=")
        try:
            value = float(mass)
        except ValueError:
            value = math.nan
        if not sep or not particle.strip() or not math.isfinite(value) or value < 0:
            raise InputError(f"--mass {item!r}: use PARTICLE=GEV, e.g. --mass gluino=1750")
        name = canonical_particle(particle)
        if name is None:
            raise InputError(
                f"--mass {item!r}: unknown particle; use one of {', '.join(PARTICLES)}"
            )
        masses[name] = value
    return masses


def _parse_process(text: str | None) -> str | None:
    if text is None:
        return None
    process = canonical_process(text)
    if process is None:
        raise InputError(f"--process {text!r}: unknown; use one of {', '.join(PROCESSES)}")
    return process


def _check_unit(kind: str, unit_text: str | None) -> str:
    expected = _EXPECTED_AREA_POWER[kind]
    if unit_text is None:
        if expected != 0:
            raise InputError(f"{kind}: --unit is required ({_UNIT_HINT[expected]})")
        return "dimensionless"
    try:
        unit = parse_unit(unit_text)
    except UnitError as exc:
        raise InputError(f"{kind}: {exc}") from exc
    if unit.area_power != expected:
        raise InputError(f"{kind}: unit {unit_text!r} is wrong here; use {_UNIT_HINT[expected]}")
    return unit.name


def _check_range(kind: str, value: float, reason: str | None) -> None:
    if not math.isfinite(value) or value <= 0:
        raise InputError(f"{kind}: value must be a positive number, got {value}")
    if kind in (BRANCHING_FRACTION, EFFICIENCY):
        if value > 1:
            raise InputError(f"{kind}: must be at most 1, got {value}")
        if value == 1 and not (reason and reason.strip()):
            raise InputError(f"{kind}: a value of exactly 1 needs --reason (why is it 1?)")


def _check_counts(value: float, n_pass: float | None, n_gen: float | None) -> None:
    if (n_pass is None) != (n_gen is None):
        raise InputError("efficiency: give both --n-pass and --n-gen, or neither")
    if n_pass is None or n_gen is None:
        return
    if not n_gen > 0 or not 0 <= n_pass <= n_gen:
        raise InputError(
            f"efficiency: need 0 <= n_pass <= n_gen and n_gen > 0, got {n_pass}/{n_gen}"
        )
    ratio = n_pass / n_gen
    if abs(value - ratio) > EPS_MATCH * ratio:
        raise InputError(
            f"efficiency: value {value:g} does not match n_pass/n_gen = {ratio:g}; "
            "record scale factors separately with `record-quantity correction`"
        )


def build_entry(args: argparse.Namespace) -> Entry:
    """Validate the arguments for one quantity or correction and return the Entry."""
    kind: str = args.name
    if args.value is None:
        raise InputError(f"{kind}: --value is required")
    if not (args.source and args.source.strip()):
        raise InputError(f"{kind}: --source is required (tool and settings, table, or page)")
    unit = _check_unit(kind, args.unit)
    _check_range(kind, args.value, args.reason)
    source_type = args.source_type
    if kind == GENERATOR_CROSS_SECTION and source_type is None:
        source_type = "generator"
    if kind in _NEEDS_SOURCE_TYPE and source_type is None:
        raise InputError(f"{kind}: --source-type is required ({', '.join(sorted(SOURCE_TYPES))})")
    if kind == EFFICIENCY:
        _check_counts(args.value, args.n_pass, args.n_gen)
    elif args.n_pass is not None or args.n_gen is not None:
        raise InputError(f"{kind}: --n-pass/--n-gen belong to efficiency only")
    if kind == CORRECTION and not (args.label and args.label.strip()):
        raise InputError("correction: --name is required, e.g. --name trigger")
    return Entry(
        name=args.label.strip() if kind == CORRECTION else kind,
        value=args.value,
        unit=unit,
        source=args.source.strip(),
        source_type=source_type,
        process=_parse_process(args.process),
        masses_gev=_parse_masses(args.mass),
        reason=args.reason.strip() if args.reason else None,
        n_pass=args.n_pass,
        n_gen=args.n_gen,
        uncertainty=args.uncertainty,
    )


def record(ledger: Ledger, kind: str, entry: Entry) -> Ledger:
    """Return a copy of `ledger` with `entry` added; the last value for a name wins."""
    if kind == CORRECTION:
        kept = tuple(c for c in ledger.corrections if c.name != entry.name)
        return replace(ledger, schema_version=SCHEMA_VERSION, corrections=(*kept, entry))
    quantities = {**ledger.quantities, kind: entry}
    return replace(ledger, schema_version=SCHEMA_VERSION, quantities=quantities)


def _line(entry: Entry) -> str:
    value = "-" if entry.value is None else f"{entry.value:.6g}"
    parts = [f"{entry.name:22s} {value} {entry.unit or '(no unit)'}"]
    if entry.n_pass is not None and entry.n_gen is not None:
        parts.append(f"[{entry.n_pass:g}/{entry.n_gen:g}]")
    if entry.masses_gev:
        parts.append("@ " + ", ".join(f"{k}={v:g}" for k, v in entry.masses_gev.items()))
    parts.append(f"<- {entry.source or '(no source)'}")
    return " ".join(parts)


def show(ledger: Ledger, path: Path) -> str:
    """Human-readable ledger plus the agent's own formula product."""
    lines = [f"ledger: {path}"]
    lines += [_line(ledger.quantities[n]) for n in QUANTITY_NAMES if n in ledger.quantities]
    lines += ["correction: " + _line(c) for c in ledger.corrections]
    missing = ledger.missing_factors()
    if missing:
        lines.append(f"formula: incomplete, missing {', '.join(missing)}")
        return "\n".join(lines)
    try:
        product = ledger.product()
    except (ValueError, UnitError) as exc:
        lines.append(f"formula: cannot compute ({exc})")
        return "\n".join(lines)
    names = "*".join(("sigma", "L", "BR", "eps", *(c.name for c in ledger.corrections)))
    if product.unit_free:
        lines.append(f"formula: {names} = {product.value:.6g} expected events")
    else:
        lines.append(
            f"formula: {names} = {product.value:.6g}, but units do not cancel "
            f"(area power {product.area_power:+d})"
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Exit 0 on success, 1 on refused input or a broken ledger file."""
    args = _parser().parse_args(argv)
    path = _ledger_path(args.ledger)
    try:
        if path.exists():
            ledger = load_ledger(path)
        else:
            ledger = empty_ledger(os.environ.get("TRUSTLAYER_TASK"))
        if args.name == SHOW:
            print(show(ledger, path))
            return 0
        entry = build_entry(args)
        save_ledger(record(ledger, args.name, entry), path)
    except (InputError, LedgerError) as exc:
        print(f"record-quantity: {exc}", file=sys.stderr)
        return 1
    print(f"recorded {_line(entry)}\n  -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
