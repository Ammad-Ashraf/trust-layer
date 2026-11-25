"""Load the two non-ledger inputs of the checks: the public task context and the submission.

Task context: `integration/task-context/<task>.yaml`, built only from the agent-visible task
card. Submission: the agent's filled `results/*.yaml` (two YAML documents: metadata, then the
HEPData-style histogram whose `dependent_variables[0].values[*].value` are the bin yields).
Both loaders fail loudly with InputsError naming the problem.
"""

from __future__ import annotations

import math
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from trustlayer.ledger.names import canonical_particle, canonical_process


class InputsError(ValueError):
    """A task context or results file that can't be read or has the wrong shape."""


@dataclass(frozen=True)
class TaskContext:
    """Public facts about one task: its signal process, masses and luminosity."""

    task: str
    luminosity_fb: float
    process: str
    sigma_masses_gev: Mapping[str, float]
    masses_gev: Mapping[str, float] = field(default_factory=dict)
    benchmark: str | None = None


@dataclass(frozen=True)
class Submission:
    """The agent's submitted bin yields (None for a bin left unfilled)."""

    path: Path
    bins: tuple[float | None, ...]


def _read_yaml_docs(path: Path) -> list[object]:
    try:
        return list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except OSError as exc:
        raise InputsError(f"{path}: cannot read ({exc.strerror or exc})") from exc
    except yaml.YAMLError as exc:
        raise InputsError(f"{path}: not valid YAML ({exc})") from exc


def _masses(raw: object, where: str) -> dict[str, float]:
    if not isinstance(raw, Mapping):
        raise InputsError(f"{where}: must be a mapping of particle -> GeV")
    out: dict[str, float] = {}
    for particle, mass in raw.items():
        name = canonical_particle(str(particle))
        if name is None or isinstance(mass, bool) or not isinstance(mass, int | float):
            raise InputsError(f"{where}.{particle}: unknown particle or non-numeric mass")
        out[name] = float(mass)
    return out


def load_task_context(path: str | os.PathLike[str]) -> TaskContext:
    """Load one task-context file. Raises InputsError on any missing or malformed field."""
    p = Path(path)
    docs = _read_yaml_docs(p)
    data = docs[0] if len(docs) == 1 else None
    if not isinstance(data, Mapping):
        raise InputsError(f"{p}: must be one YAML mapping")
    signal = data.get("signal")
    lumi = data.get("luminosity_fb")
    task = data.get("task")
    if not isinstance(task, str) or not isinstance(signal, Mapping):
        raise InputsError(f"{p}: needs `task` and a `signal` mapping")
    if isinstance(lumi, bool) or not isinstance(lumi, int | float) or lumi <= 0:
        raise InputsError(f"{p}: `luminosity_fb` must be a positive number")
    process = canonical_process(str(signal.get("process", "")))
    if process is None:
        raise InputsError(f"{p}: signal.process {signal.get('process')!r} is not a known process")
    sigma_masses = _masses(signal.get("sigma_masses_gev"), f"{p}: signal.sigma_masses_gev")
    if not sigma_masses:
        raise InputsError(f"{p}: signal.sigma_masses_gev is empty")
    masses = _masses(signal.get("masses_gev", sigma_masses), f"{p}: signal.masses_gev")
    benchmark = signal.get("benchmark")
    return TaskContext(
        task=task,
        luminosity_fb=float(lumi),
        process=process,
        sigma_masses_gev=sigma_masses,
        masses_gev={**masses, **sigma_masses},
        benchmark=benchmark if isinstance(benchmark, str) else None,
    )


def load_submission(path: str | os.PathLike[str]) -> Submission:
    """Read the bin values from a filled results template. Raises InputsError if malformed."""
    p = Path(path)
    docs = [d for d in _read_yaml_docs(p) if d is not None]
    hist = next(
        (d for d in reversed(docs) if isinstance(d, Mapping) and "dependent_variables" in d), None
    )
    if hist is None:
        raise InputsError(f"{p}: no `dependent_variables` block found")
    try:
        values = hist["dependent_variables"][0]["values"]
    except (KeyError, IndexError, TypeError) as exc:
        raise InputsError(f"{p}: expected dependent_variables[0].values") from exc
    if not isinstance(values, list) or not values:
        raise InputsError(f"{p}: dependent_variables[0].values must be a non-empty list")
    bins: list[float | None] = []
    for i, item in enumerate(values):
        raw = item.get("value") if isinstance(item, Mapping) else None
        if raw is None:
            bins.append(None)
        elif isinstance(raw, bool) or not isinstance(raw, int | float) or not math.isfinite(raw):
            raise InputsError(f"{p}: bin {i + 1} value {raw!r} is not a finite number")
        else:
            bins.append(float(raw))
    return Submission(path=p, bins=tuple(bins))
