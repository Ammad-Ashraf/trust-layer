"""Find the gate's inputs from the agent's working directory.

Collider-Bench runs the agent in `<repo>/runs/<runner>_<model>/<task>_<agent-id>/workspace/`,
so the task id is the prefix of the run folder's name. Only agent-visible files are read:
`<workspace>/ledger.yaml`, `<workspace>/results/*.yaml`, and the public task context shipped
in the agent folder's `runtime/task-context/`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

LEDGER_NAME = "ledger.yaml"


class LocateError(LookupError):
    """The gate can't find something it needs that isn't the agent's fault."""


@dataclass(frozen=True)
class GatePaths:
    """Absolute paths the gate reads (results may be None, with the reason in results_error)."""

    workspace: Path
    ledger: Path
    results: Path | None
    results_error: str | None
    task_context: Path


def _run_folder_name(workspace: Path) -> str:
    return workspace.parent.name if workspace.name == "workspace" else workspace.name


def find_task_context(workspace: Path, contexts_dir: Path) -> Path:
    """The task-context file whose task id prefixes the run folder's name (longest match)."""
    run_name = _run_folder_name(workspace)
    candidates = sorted(contexts_dir.glob("*.yaml")) if contexts_dir.is_dir() else []
    matches = [p for p in candidates if run_name == p.stem or run_name.startswith(p.stem + "_")]
    if not matches:
        raise LocateError(
            f"no task context in {contexts_dir} matches run folder {run_name!r}; "
            "set TRUSTLAYER_TASK_CONTEXT"
        )
    return max(matches, key=lambda p: len(p.stem))


def _results(workspace: Path, env: Mapping[str, str]) -> tuple[Path | None, str | None]:
    override = env.get("TRUSTLAYER_RESULTS")
    if override:
        return Path(override).resolve(), None
    found = sorted((workspace / "results").glob("*.yaml"))
    if not found:
        return None, f"no results/*.yaml in {workspace}"
    if len(found) > 1:
        names = ", ".join(p.name for p in found)
        return None, f"several results files ({names}); the checker expects one"
    return found[0].resolve(), None


def locate(cwd: Path, env: Mapping[str, str]) -> GatePaths:
    """Resolve every input path. Raises LocateError when the task context can't be found."""
    workspace = cwd.resolve()
    ledger = Path(env.get("TRUSTLAYER_LEDGER") or workspace / LEDGER_NAME).resolve()
    results, results_error = _results(workspace, env)
    explicit = env.get("TRUSTLAYER_TASK_CONTEXT")
    if explicit:
        context = Path(explicit).resolve()
        if not context.is_file():
            raise LocateError(f"TRUSTLAYER_TASK_CONTEXT={explicit} is not a file")
    else:
        runtime = env.get("TRUSTLAYER_RUNTIME")
        if not runtime:
            raise LocateError("neither TRUSTLAYER_TASK_CONTEXT nor TRUSTLAYER_RUNTIME is set")
        context = find_task_context(workspace, Path(runtime) / "task-context")
    return GatePaths(workspace, ledger, results, results_error, context)
