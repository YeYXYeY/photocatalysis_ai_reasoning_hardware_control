"""Workflow registry for multi-device operations."""

from .standard import KNOWN_WORKFLOWS, run_named_workflow

__all__ = ["KNOWN_WORKFLOWS", "run_named_workflow"]
