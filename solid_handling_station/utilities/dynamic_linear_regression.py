"""Optional incremental dispensing calibration; not used by the active weighing loop.

Original implementation author: Ye Yuanxiang. No trained model is distributed.
Only load pickle files that you created or independently trust.
"""

from pathlib import Path
import pickle

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDRegressor
from sklearn.utils.validation import check_is_fitted

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DynamicLinearRegression:
    def __init__(self, chemical_name, *, model_dir=None, coordinates_dir=None, random_state=None):
        coordinates = Path(coordinates_dir) if coordinates_dir else PROJECT_ROOT / "coordinates"
        chemicals = pd.read_excel(coordinates / "head.xlsx")["Chemical"].dropna().tolist()
        if chemical_name not in chemicals:
            raise ValueError(f"Unknown chemical: {chemical_name}")
        if Path(str(chemical_name)).name != str(chemical_name) or any(
            c in str(chemical_name) for c in "/\\"
        ):
            raise ValueError("Chemical identifier must not contain a path separator.")
        directory = (Path(model_dir) if model_dir else PROJECT_ROOT / "model") / str(chemical_name)
        directory.mkdir(parents=True, exist_ok=True)
        self.model_filename = directory / "model.pkl"
        self.data_filename = directory / "training_data.pkl"
        self.random_state = random_state
        self.load_model_and_data()

    def save_model_and_data(self):
        with self.model_filename.open("wb") as stream:
            pickle.dump(self.model, stream)
        with self.data_filename.open("wb") as stream:
            pickle.dump((self.X, self.y), stream)

    def load_model_and_data(self):
        try:
            with self.model_filename.open("rb") as stream:
                self.model = pickle.load(stream)
            with self.data_filename.open("rb") as stream:
                self.X, self.y = pickle.load(stream)
        except (FileNotFoundError, EOFError):
            self.model = SGDRegressor(max_iter=1000, tol=1e-3, random_state=self.random_state)
            self.X = np.empty((0, 1))
            self.y = np.array([])

    def update(self, new_X_value, new_y_value):
        if not np.isfinite([new_X_value, new_y_value]).all():
            raise ValueError("Calibration values must be finite.")
        new_X = np.array([[new_X_value]])
        new_y = np.array([new_y_value])
        self.model.partial_fit(new_X, new_y)
        self.X = np.vstack((self.X, new_X))
        self.y = np.concatenate((self.y, new_y))
        self.save_model_and_data()

    def predict(self, target_y):
        check_is_fitted(self.model)
        if not np.isfinite(target_y) or np.isclose(self.model.coef_, 0).any():
            raise ValueError("Cannot invert a zero slope or a non-finite target.")
        return (target_y - self.model.intercept_) / self.model.coef_

    def update_and_predict(self, new_X_value, new_y_value, target_y):
        self.update(new_X_value, new_y_value)
        return self.predict(target_y)
