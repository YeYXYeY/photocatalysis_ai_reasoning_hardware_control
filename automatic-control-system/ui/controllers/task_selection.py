from dataclasses import dataclass


STEP_LABELS = {
    "c1": "open cap",
    "c2": "weighing",
    "c3": "liquid",
    "c4": "close cap",
    "c5": "reaction",
    "c6": "open cap",
    "c7": "liquid",
    "c8": "pre nmr",
    "c9": "close cap",
    "c10": "open cap",
    "c11": "post nmr",
    "c12": "close cap",
}


@dataclass(frozen=True)
class SelectionState:
    is_file_loaded: bool
    pre_selected: bool
    post_selected: bool
    steps: dict[str, bool]

    STEP_KEYS = tuple(STEP_LABELS.keys())


@dataclass(frozen=True)
class SelectionResult:
    is_valid: bool
    message: str


def describe_selection(state: SelectionState) -> SelectionResult:
    """Validate and describe the current task selection state."""
    if not state.is_file_loaded:
        return SelectionResult(False, "Please load a task file first")

    if state.pre_selected and state.post_selected:
        return SelectionResult(False, "Both pre and post workflows are selected")
    if state.pre_selected:
        return SelectionResult(True, "Pre-reaction workflow selected")
    if state.post_selected:
        return SelectionResult(True, "Post-reaction workflow selected")

    selected_steps = [key for key, value in state.steps.items() if value]
    if len(selected_steps) != 1:
        return SelectionResult(False, "Single-step execution requires exactly one option")

    selected_key = selected_steps[0]
    return SelectionResult(True, f"Selected step: {STEP_LABELS[selected_key]}")
