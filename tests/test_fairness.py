"""Fairness guard: the checker may only use what the agent can see.

The checker must never read Collider-Bench's internals (hidden answers, evaluator
targets) directly. Its inputs are the ledger, the agent's workspace and public task
data. This test fails if any checker source file refers to the submodule path or to
known hidden-answer locations. Extend FORBIDDEN once the smoke run shows where
Collider-Bench keeps its hidden answers.
"""

from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "trustlayer"

FORBIDDEN = [
    "external/collider-bench",
    "external\\collider-bench",
]


def test_checker_never_references_collider_bench_internals() -> None:
    offenders = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        offenders += [f"{path.name}: {pattern}" for pattern in FORBIDDEN if pattern in text]
    assert not offenders, f"Checker code references forbidden paths: {offenders}"
