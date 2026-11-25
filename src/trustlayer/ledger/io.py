"""Read and write ledger YAML files (schema versions 1 and 2).

Loading is strict about structure (wrong types raise LedgerError naming the field) and
permissive about content (missing values load as None, so the checks can report them).
Saving is atomic: write a temp file next to the target, then rename over it.
"""

from __future__ import annotations

import math
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from trustlayer.ledger.model import (
    QUANTITY_NAMES,
    SUPPORTED_VERSIONS,
    Entry,
    Ledger,
    LedgerError,
)

_ENTRY_KEYS = (
    "value",
    "unit",
    "uncertainty",
    "source",
    "source_type",
    "process",
    "masses_gev",
    "reason",
    "n_pass",
    "n_gen",
)
_TOP_KEYS = ("schema_version", "task", "quantities", "corrections")


def _number(raw: object, where: str) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, bool) or not isinstance(raw, int | float):
        raise LedgerError(f"{where}: must be a number, got {raw!r}")
    value = float(raw)
    if not math.isfinite(value):
        raise LedgerError(f"{where}: must be finite, got {raw!r}")
    return value


def _text(raw: object, where: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise LedgerError(f"{where}: must be text, got {raw!r}")
    return raw


def _masses(raw: object, where: str) -> dict[str, float]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise LedgerError(f"{where}: must be a mapping of particle -> mass in GeV")
    out: dict[str, float] = {}
    for particle, mass in raw.items():
        value = _number(mass, f"{where}.{particle}")
        if value is None:
            raise LedgerError(f"{where}.{particle}: mass is missing")
        out[str(particle)] = value
    return out


def _entry(name: str, raw: object, where: str) -> Entry:
    if not isinstance(raw, Mapping):
        raise LedgerError(f"{where}: must be a mapping with value, unit and source")
    return Entry(
        name=name,
        value=_number(raw.get("value"), f"{where}.value"),
        unit=_text(raw.get("unit"), f"{where}.unit"),
        source=_text(raw.get("source"), f"{where}.source"),
        source_type=_text(raw.get("source_type"), f"{where}.source_type"),
        process=_text(raw.get("process"), f"{where}.process"),
        masses_gev=_masses(raw.get("masses_gev"), f"{where}.masses_gev"),
        reason=_text(raw.get("reason"), f"{where}.reason"),
        n_pass=_number(raw.get("n_pass"), f"{where}.n_pass"),
        n_gen=_number(raw.get("n_gen"), f"{where}.n_gen"),
        uncertainty=_number(raw.get("uncertainty"), f"{where}.uncertainty"),
        extra={k: v for k, v in raw.items() if k not in _ENTRY_KEYS and k != "name"},
    )


def ledger_from_dict(data: object) -> Ledger:
    """Build a Ledger from parsed YAML. Raises LedgerError on structural problems."""
    if not isinstance(data, Mapping):
        raise LedgerError("ledger: top level must be a mapping")
    version = data.get("schema_version")
    if (
        isinstance(version, bool)
        or not isinstance(version, int)
        or version not in SUPPORTED_VERSIONS
    ):
        raise LedgerError(f"schema_version: must be one of {SUPPORTED_VERSIONS}, got {version!r}")

    raw_quantities = data.get("quantities")
    if raw_quantities is None:
        raw_quantities = {}
    if not isinstance(raw_quantities, Mapping):
        raise LedgerError("quantities: must be a mapping")
    quantities: dict[str, Entry] = {}
    for name, raw in raw_quantities.items():
        if name not in QUANTITY_NAMES:
            raise LedgerError(f"quantities.{name}: unknown; allowed: {', '.join(QUANTITY_NAMES)}")
        quantities[name] = _entry(name, raw, f"quantities.{name}")

    raw_corrections = data.get("corrections")
    if raw_corrections is None:
        raw_corrections = []
    if not isinstance(raw_corrections, list):
        raise LedgerError("corrections: must be a list")
    corrections: list[Entry] = []
    for i, raw in enumerate(raw_corrections):
        where = f"corrections[{i}]"
        label = _text(raw.get("name") if isinstance(raw, Mapping) else None, f"{where}.name")
        if not label:
            raise LedgerError(f"{where}.name: every correction needs a name")
        corrections.append(_entry(label, raw, where))

    return Ledger(
        schema_version=version,
        task=_text(data.get("task"), "task"),
        quantities=quantities,
        corrections=tuple(corrections),
        extra={k: v for k, v in data.items() if k not in _TOP_KEYS},
    )


def _entry_to_dict(entry: Entry, *, with_name: bool = False) -> dict[str, Any]:
    out: dict[str, Any] = {"name": entry.name} if with_name else {}
    out["value"] = entry.value
    out["unit"] = entry.unit
    optional: dict[str, Any] = {
        "uncertainty": entry.uncertainty,
        "source": entry.source,
        "source_type": entry.source_type,
        "process": entry.process,
        "masses_gev": dict(entry.masses_gev) or None,
        "reason": entry.reason,
        "n_pass": entry.n_pass,
        "n_gen": entry.n_gen,
    }
    out.update({k: v for k, v in optional.items() if v is not None})
    out.update(entry.extra)
    return out


def ledger_to_dict(ledger: Ledger) -> dict[str, Any]:
    """The YAML-ready form of a ledger. Inverse of ledger_from_dict."""
    out: dict[str, Any] = {"schema_version": ledger.schema_version, "task": ledger.task}
    out["quantities"] = {n: _entry_to_dict(e) for n, e in ledger.quantities.items()}
    if ledger.corrections:
        out["corrections"] = [_entry_to_dict(c, with_name=True) for c in ledger.corrections]
    out.update(ledger.extra)
    return out


def load_ledger(path: str | os.PathLike[str]) -> Ledger:
    """Load a ledger file. Raises LedgerError (bad structure or YAML) or FileNotFoundError."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise LedgerError(f"{path}: not valid YAML ({exc})") from exc
    return ledger_from_dict(data)


def save_ledger(ledger: Ledger, path: str | os.PathLike[str]) -> None:
    """Write a ledger atomically. Comments in an existing file are not kept."""
    target = Path(path)
    text = yaml.safe_dump(ledger_to_dict(ledger), sort_keys=False, allow_unicode=True)
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, target)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
