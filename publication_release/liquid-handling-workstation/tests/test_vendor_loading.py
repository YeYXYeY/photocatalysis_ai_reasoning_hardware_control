import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


class VendorLoadingTests(unittest.TestCase):
    def test_import_does_not_load_the_vendor_library(self):
        path = Path(__file__).resolve().parents[1] / "devices/zmotion/zauxdllPython.py"
        spec = importlib.util.spec_from_file_location("vendor_bindings_test", path)
        module = importlib.util.module_from_spec(spec)
        with patch("ctypes.WinDLL", create=True) as loader:
            spec.loader.exec_module(module)
        loader.assert_not_called()
        self.assertIsNone(module.zauxdll.library)

    def test_missing_vendor_library_has_an_actionable_error(self):
        path = Path(__file__).resolve().parents[1] / "devices/zmotion/zauxdllPython.py"
        spec = importlib.util.spec_from_file_location("vendor_bindings_missing_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with (
            patch("platform.system", return_value="Windows"),
            patch.dict("os.environ", {"ZMOTION_LIBRARY": str(path.parent / "missing-runtime.dll")}),
        ):
            with self.assertRaisesRegex(FileNotFoundError, "ZMOTION_LIBRARY"):
                module.zauxdll.ZAux_OpenEth
