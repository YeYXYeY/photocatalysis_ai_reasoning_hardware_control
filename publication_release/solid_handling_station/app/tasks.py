"""Pure task validation; importing this module never initializes hardware."""

from collections import OrderedDict

import numpy as np
import pandas as pd


def build_chemical_tasks(dataframe):
    """Validate a NO-by-reagent table and return nonempty positive-mass tasks.

    NO contains unique positive integer bottle identifiers. Other columns contain
    target masses in mg; blank cells and zero mean no dispensing action.
    """
    if "NO" not in dataframe.columns or len(dataframe.columns) < 2:
        raise ValueError("Task workbook requires NO and at least one reagent column.")
    if dataframe.empty or not dataframe.columns.is_unique:
        raise ValueError("Task workbook must contain rows and unique column names.")
    numbers = pd.to_numeric(dataframe["NO"], errors="raise")
    if (
        not np.isfinite(numbers).all()
        or (numbers <= 0).any()
        or (numbers % 1 != 0).any()
        or numbers.duplicated().any()
    ):
        raise ValueError("Bottle identifiers must be unique positive integers.")
    tasks = OrderedDict()
    for chemical in dataframe.columns:
        if chemical == "NO":
            continue
        values = pd.to_numeric(dataframe[chemical], errors="raise")
        present = values.notna()
        if not np.isfinite(values[present]).all() or (values[present] < 0).any():
            raise ValueError(f"Target masses for {chemical} must be finite and non-negative.")
        active = present & (values > 0)
        if active.any():
            tasks[chemical] = {
                "TargetWeight": values[active].tolist(),
                "BottleNum": numbers[active].astype(int).tolist(),
            }
    if not tasks:
        raise ValueError("Task workbook contains no positive target masses.")
    return tasks
