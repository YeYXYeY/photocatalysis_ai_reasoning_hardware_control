import importlib
import sys
import types
import unittest
from pathlib import Path


def build_fake_yaml_module():
    fake_yaml = types.ModuleType("yaml")

    class FakeYAMLError(Exception):
        pass

    def safe_load(stream):
        return {"RS485": {}, "controller": {}, "peristaltic_pump": {}}

    fake_yaml.safe_load = safe_load
    fake_yaml.YAMLError = FakeYAMLError
    return fake_yaml


def build_fake_pandas_module(read_calls):
    fake_pandas = types.ModuleType("pandas")

    def read_excel(path):
        path = Path(path)
        read_calls.append(path)
        return {"path": str(path)}

    fake_pandas.read_excel = read_excel
    return fake_pandas


class LiquidStationRuntimeTests(unittest.TestCase):
    def load_module(self, read_calls=None):
        sys.modules["yaml"] = build_fake_yaml_module()
        tracked_calls = read_calls if read_calls is not None else []
        sys.modules["pandas"] = build_fake_pandas_module(tracked_calls)

        sys.modules.pop("utils.config", None)
        sys.modules.pop("devices.liquid_station_runtime", None)
        return importlib.import_module("devices.liquid_station_runtime")

    def test_build_liquid_station_paths_uses_project_conventions(self):
        runtime_module = self.load_module()

        paths = runtime_module.build_liquid_station_paths(
            Path("C:/lab/liquid-handling-workstation/devices")
        )

        self.assertEqual(
            paths.project_root,
            Path("C:/lab/liquid-handling-workstation"),
        )
        self.assertEqual(
            paths.coordinates_dir,
            Path("C:/lab/liquid-handling-workstation/coordinates"),
        )
        self.assertEqual(
            paths.tip_for_pump_path,
            Path("C:/lab/liquid-handling-workstation/coordinates/tip_for_pump.xlsx"),
        )

    def test_build_coordinate_workbook_paths_lists_expected_assets(self):
        runtime_module = self.load_module()
        paths = runtime_module.build_liquid_station_paths(
            Path("C:/lab/liquid-handling-workstation/devices")
        )

        workbook_paths = runtime_module.build_coordinate_workbook_paths(paths)

        self.assertIn("reagent_df", workbook_paths)
        self.assertIn("reaction_for_gripper_df", workbook_paths)
        self.assertEqual(
            workbook_paths["dosing_head_df"],
            Path("C:/lab/liquid-handling-workstation/coordinates/dosing_head.xlsx"),
        )

    def test_load_coordinate_tables_reads_every_known_workbook(self):
        read_calls = []
        runtime_module = self.load_module(read_calls=read_calls)
        paths = runtime_module.build_liquid_station_paths(
            Path("C:/lab/liquid-handling-workstation/devices")
        )

        tables = runtime_module.load_coordinate_tables(paths)

        self.assertEqual(set(tables), set(runtime_module.build_coordinate_workbook_paths(paths)))
        self.assertEqual(read_calls[0].name, "reagent.xlsx")
        self.assertEqual(read_calls[-1].name, "tip_for_pump.xlsx")


if __name__ == "__main__":
    unittest.main()
