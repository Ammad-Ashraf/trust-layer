"""Fairness guard: the checker may only use what the agent can see.

1. Checker source never refers to Collider-Bench internals (hidden answers, evaluator targets).
   Collider-Bench keeps its hidden answers under `ColliderBench/tasks/shared/<paper>/reference/`
   (confirmed in the 2026-11-18 smoke run).
2. The built `simple_ledger` agent folder (what goes into the container) carries nothing from
   tasks/, docs/, CLAUDE.md, .claude/ or papers/notes/, and no answer-key values.
3. Task-context files hold only public task-card facts.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "trustlayer"
CONTEXTS = ROOT / "integration" / "task-context"

FORBIDDEN = [
    "external/collider-bench",
    "external\\collider-bench",
    "ColliderBench/tasks",
    "ColliderBench\\tasks",
    "tasks/shared",
    "tasks\\shared",
]
ANSWER_KEYS = ("expected_events", "per_bin", "reference", "efficiency", "yield")


def test_checker_never_references_collider_bench_internals() -> None:
    offenders = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        offenders += [f"{path.name}: {pattern}" for pattern in FORBIDDEN if pattern in text]
    assert not offenders, f"Checker code references forbidden paths: {offenders}"


def _load_build_script():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location(
        "build_agent_folder", ROOT / "scripts" / "build_agent_folder.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("agent") / "simple_ledger"
    return Path(_load_build_script().build(out))


def test_built_folder_has_no_builder_or_answer_files(built: Path) -> None:
    names = {p.name for p in built.rglob("*")}
    assert not names & {"CLAUDE.md", ".claude", "ledger.yaml", "story.md", "project-summary.md"}
    hand_ledgers = [p.read_bytes() for p in (ROOT / "tasks").rglob("*") if p.is_file()]
    for path in built.rglob("*"):
        if path.is_file():
            assert path.read_bytes() not in hand_ledgers, f"{path} is a copy of a tasks/ file"


def test_built_folder_contains_no_answer_values(built: Path) -> None:
    hand = yaml.safe_load(
        (ROOT / "tasks" / "sus-16-034_sim-TChiWZ" / "ledger.yaml").read_text("utf-8")
    )
    secrets = [
        "Additional Table 7",
        "0.0495",
        "0.04947",
        "5.41",
        str(hand["expected_events"]["per_bin"]["150-250"]),
    ]
    for path in built.rglob("*"):
        if path.is_file() and path.suffix in {".yaml", ".md", ".py", ""}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            leaked = [s for s in secrets if s in text]
            assert not leaked, f"{path.relative_to(built)} contains answer values {leaked}"


def test_built_folder_layout(built: Path) -> None:
    for rel in (
        "run.py",
        "AGENTS.md",
        "runtime/bin/record-quantity",
        "runtime/bin/run-analysis",
        "runtime/hooks/trustlayer-gate",
        "runtime/lib/trustlayer/gate/hook.py",
        "runtime/config.yaml",
        "runtime/BUILD-INFO.yaml",
    ):
        assert (built / rel).is_file(), rel
    assert "## Normalization ledger (required)" in (built / "AGENTS.md").read_text("utf-8")
    assert (
        yaml.safe_load((built / "runtime" / "config.yaml").read_text("utf-8"))["c5_tolerance"]
        == 0.05
    )
    assert b"\r\n" not in (built / "runtime" / "hooks" / "trustlayer-gate").read_bytes()


def test_task_contexts_hold_only_public_facts() -> None:
    allowed_top = {"schema_version", "task", "public_source", "luminosity_fb", "signal"}
    allowed_signal = {"benchmark", "process", "sigma_masses_gev", "masses_gev"}
    for path in CONTEXTS.glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert set(data) <= allowed_top, path.name
        assert set(data["signal"]) <= allowed_signal, path.name
        text = path.read_text(encoding="utf-8").lower()
        assert not [k for k in ANSWER_KEYS if f"{k}:" in text], path.name


def test_build_refuses_to_write_into_the_submodule() -> None:
    module = _load_build_script()
    with pytest.raises(module.BuildError, match="refusing"):
        module.build(ROOT / "external" / "collider-bench" / "agents" / "simple_ledger")
