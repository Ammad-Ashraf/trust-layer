"""Canonical particle and process names, so C4 can compare the ledger with the task.

The CLI turns common spellings (PDG ids, MadGraph names, `chi10`, ...) into one canonical
name and refuses anything it doesn't know, so a typo can't silently pass the match check.
Task facts using these names live in `integration/task-context/`.
"""

from __future__ import annotations

_PARTICLE_ALIASES: dict[str, tuple[str, ...]] = {
    "gluino": ("1000021", "go", "~g", "g~", "gl"),
    "squark": ("sq", "~q", "q~"),
    "stop_1": ("1000006", "t1", "~t1", "~t_1", "st1", "stop", "stop1"),
    "stop_2": ("2000006", "t2", "~t2", "~t_2", "stop2"),
    "sbottom_1": ("1000005", "b1", "~b1", "~b_1", "sbottom", "sbottom1"),
    "chargino_1": ("1000024", "x1+", "x1", "c1", "chi1+", "~chi_1+", "chargino", "chargino1"),
    "chargino_2": ("1000037", "x2+", "c2", "chi2+", "~chi_2+", "chargino2"),
    "neutralino_1": (
        "1000022",
        "n1",
        "chi10",
        "~chi_10",
        "neutralino",
        "neutralino1",
        "lsp_neutralino",
    ),
    "neutralino_2": ("1000023", "n2", "chi20", "~chi_20", "neutralino2"),
    "neutralino_3": ("1000025", "n3", "chi30", "~chi_30", "neutralino3"),
    "neutralino_4": ("1000035", "n4", "chi40", "~chi_40", "neutralino4"),
    "gravitino": ("1000039", "~g_3/2", "gr", "grav"),
    "slepton": ("sl", "~l"),
}

PARTICLES = tuple(_PARTICLE_ALIASES)
"""Canonical particle names."""

PROCESSES = (
    "gluino_pair",
    "squark_pair",
    "squark_gluino",
    "stop_pair",
    "sbottom_pair",
    "chargino_neutralino",
    "chargino_pair",
    "neutralino_pair",
    "slepton_pair",
)
"""Canonical production-process tokens for the cross section."""

_LOOKUP: dict[str, str] = {
    alias: name for name, aliases in _PARTICLE_ALIASES.items() for alias in (name, *aliases)
}


def canonical_particle(text: str) -> str | None:
    """Canonical name for a particle spelling, or None if unknown (case and spaces ignored)."""
    key = text.strip().lower().replace(" ", "").replace("-", "_")
    return _LOOKUP.get(key) or _LOOKUP.get(key.replace("_", ""))


def canonical_process(text: str) -> str | None:
    """Canonical process token, or None if unknown."""
    key = text.strip().lower().replace(" ", "_").replace("-", "_")
    return key if key in PROCESSES else None
