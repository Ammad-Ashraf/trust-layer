"""Injector: makes broken copies of correct ledgers with one known 1a-1e mistake each (Study A).

The list of mistakes is fixed by decision 0016 (plus the rows added by 0017, kept apart).
"""

from trustlayer.inject.study_a import (
    Case,
    Skipped,
    StudyConfig,
    StudyConfigError,
    TaskInputs,
    build_cases,
    load_study_config,
    load_task_inputs,
)

__all__ = [
    "Case",
    "Skipped",
    "StudyConfig",
    "StudyConfigError",
    "TaskInputs",
    "build_cases",
    "load_study_config",
    "load_task_inputs",
]
