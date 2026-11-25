"""Gate settings: the C5 tolerance and the bounce cap. Values are config, not code.

The agent-folder build writes `runtime/config.yaml` from the experiment config (decision 0016
fixes tau). The defaults below are used only when no config file exists, and the bounce log
records which values were used.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml

from trustlayer.checks.base import DEFAULT_C5_TOLERANCE

DEFAULT_MAX_BOUNCES = 3


class ConfigError(ValueError):
    """A gate config file that exists but can't be used."""


@dataclass(frozen=True)
class GateConfig:
    """C5 tolerance tau, maximum bounces before submitting with warnings, and where it came from."""

    c5_tolerance: float = DEFAULT_C5_TOLERANCE
    max_bounces: int = DEFAULT_MAX_BOUNCES
    source: str = "defaults"


def load_config(path: str | os.PathLike[str] | None) -> GateConfig:
    """Read the gate config, or return defaults when `path` is None or doesn't exist."""
    if path is None or not Path(path).is_file():
        return GateConfig()
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"{path}: cannot read gate config ({exc})") from exc
    if not isinstance(data, Mapping):
        raise ConfigError(f"{path}: gate config must be a mapping")
    tau = data.get("c5_tolerance", DEFAULT_C5_TOLERANCE)
    cap = data.get("max_bounces", DEFAULT_MAX_BOUNCES)
    if isinstance(tau, bool) or not isinstance(tau, int | float) or not 0 < tau < 1:
        raise ConfigError(f"{path}: c5_tolerance must be a number between 0 and 1")
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 0:
        raise ConfigError(f"{path}: max_bounces must be a non-negative integer")
    return GateConfig(float(tau), cap, str(path))
