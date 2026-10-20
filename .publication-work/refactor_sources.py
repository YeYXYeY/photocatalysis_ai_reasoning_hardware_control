"""Apply bounded structural changes to the independent release directory."""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'publication_release'
SOLID = ROOT / 'solid_handling_station'


def write(relative, content):
    (ROOT / relative).write_text(content, encoding='utf-8', newline='\n')


write('solid_handling_station/main.py', '''"""Command-line entrypoint. Device imports occur only after task validation."""
import argparse
from pathlib import Path

import pandas as pd

from app.tasks import build_chemical_tasks


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Execute a solid dispensing task (target masses in mg).")
    parser.add_argument("--taskfile", type=Path, required=True, help="Task workbook with NO and reagent columns.")
    parser.add_argument("--func", choices=("weighing", "start_weighing"), default="weighing")
    parser.add_argument("--output-dir", type=Path, help="Directory for measured mass output.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    dataframe = pd.read_excel(args.taskfile)
    build_chemical_tasks(dataframe)
    from app.workflow import default_output_dir, run_weighing
    from utilities.solid_weigh import SolidWeigh
    output = args.output_dir or default_output_dir(Path(__file__).parent)
    station = SolidWeigh()
    try:
        print(run_weighing(dataframe, station, output))
    finally:
        station.weighing.close()
        if station.motion.ser.is_open:
            station.motion.ser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''')

# Keep the existing motion order and hardware parameters. Remove shadowed code
# and import-time file/log setup; make runtime loading explicit and testable.
p = SOLID / 'utilities/solid_weigh.py'
source = p.read_text(encoding='utf-8')
source = source[:source.index('if __name__ == "__main__":')]
start = source.index('# Get configuration file')
end = source.index('class SolidWeigh:')
source = source[:start] + 'from app.runtime import load_station_runtime\n\n\n' + source[end:]
source = source.replace('    def __init__(self):\n', '''    def __init__(self, runtime=None):
        runtime = runtime or load_station_runtime()
        weighing_param = runtime.config["solid_weighing"]
''', 1)
source = source.replace('self.logger = logger', 'self.logger = runtime.logger')
source = source.replace('self.chemical_data_path = chemical_data_path', 'self.chemical_data_path = str(runtime.chemical_data_dir)')
source = source.replace('self.coordinates_path = coordinates_path', 'self.coordinates_path = str(runtime.coordinates_dir)')
for table in ['database_df', 'balance_coordinates_df', 'head_coordinates_df', 'reaction_coordinates_df']:
    source = source.replace(f'self.{table} = {table}', f'self.{table} = runtime.tables["{table}"]')
tree = ast.parse(source)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
duplicate = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'weighing_params')
lines = source.splitlines(keepends=True)
del lines[duplicate.lineno-1:duplicate.end_lineno]
source = ''.join(lines)
source = source.replace('self.calibrate_actuator()', 'self.calibrate_actuator(align_pos)')
source = source.replace('        self.stop_event.clear()', '''        if not 0 < target_weight < float("inf"):
            raise ValueError("Target mass must be finite and positive.")
        self.stop_event.clear()''')
p.write_text(source, encoding='utf-8')

for filename, key in [('motion.py', 'dm2c556'), ('weighing.py', 'mk210')]:
    p = SOLID / 'devices' / filename
    source = p.read_text(encoding='utf-8')
    if 'if __name__ == "__main__":' in source:
        source = source[:source.index('if __name__ == "__main__":')]
    start = source.index('current_path = ')
    end = source.index('# ', start) if filename == 'motion.py' else source.index('class Weighing:')
    if filename == 'motion.py':
        end = source.index('reset_pge = ', start)
    source = source[:start] + 'from pathlib import Path\nfrom app.runtime import load_yaml\n\n' + source[end:]
    source = source.replace('self.serial_param = serial_param', f'self.serial_param = load_yaml(Path(__file__).with_name("config.yaml"))["{key}"]')
    source = source.replace('self.logger = logger', 'self.logger = logger or logging.getLogger(__name__)')
    p.write_text(source, encoding='utf-8')

# Use the existing English logger implementation while preserving module APIs.
source = (ROOT / 'liquid-handling-workstation/utils/config.py').read_text(encoding='utf-8')
source = source.replace('liquid_workstation', 'solid_workstation')
(SOLID / 'utils/config.py').write_text(source, encoding='utf-8')
(SOLID / 'utilities/config.py').write_text('''"""Compatibility API for the solid station configuration and logger."""
from pathlib import Path
from utils.config import config_logger, load_config


def load_config_and_logger(log_file_name):
    logger = config_logger(log_file_name)
    return load_config(Path(__file__).with_name("config.yaml"), logger=logger), logger
''', encoding='utf-8')

# Remove unguarded historical demonstrations, retaining reusable functions.
for relative in ['client/master_control_client.py', 'utils/split_task.py']:
    p = SOLID / relative
    source = p.read_text(encoding='utf-8')
    source = source.split('if __name__ == "__main__":')[0]
    p.write_text(source, encoding='utf-8')
p = SOLID / 'utilities/split_task.py'
source = p.read_text(encoding='utf-8')
source = source[:source.index('file_path = "./0417task.xlsx"')]
p.write_text(source, encoding='utf-8')

# Load the supplier runtime lazily using a portable configured or adjacent path.
p = ROOT / 'liquid-handling-workstation/devices/zmotion/zauxdllPython.py'
source = p.read_text(encoding='utf-8')
body = source[source.index('class ZAUXDLL:'):]
p.write_text('''"""Python bindings for the separately installed ZMotion vendor runtime.

The original wrapper is retained; runtime binaries are supplied by the vendor.
"""
import ctypes
import os
from pathlib import Path
import platform


class _LazyVendorLibrary:
    def __init__(self):
        self.library = None
        self.dll_directory = None

    def __getattr__(self, name):
        if self.library is None:
            if platform.system() != "Windows":
                raise RuntimeError("The released ZMotion hardware integration requires Windows and a matching vendor SDK.")
            path = Path(os.environ.get("ZMOTION_LIBRARY", Path(__file__).with_name("zauxdll.dll"))).resolve()
            if not path.is_file():
                raise FileNotFoundError("Install the ZMotion runtime and set ZMOTION_LIBRARY to the absolute zauxdll.dll path.")
            if hasattr(os, "add_dll_directory"):
                self.dll_directory = os.add_dll_directory(str(path.parent))
            self.library = ctypes.WinDLL(str(path))
        return getattr(self.library, name)


zauxdll = _LazyVendorLibrary()


''' + body, encoding='utf-8')

# Select a real included task rather than an ignored runtime directory default.
p = ROOT / 'automatic-control-system/workflow/run_sample_workflow.py'
source = p.read_text(encoding='utf-8')
source = source.replace('task_file_name: str = "0923task.xlsx"', 'task_file_name: str = "hub_task.xlsx"')
source = source.replace('self.task_dir = os.path.join(self.project_root, "task")', 'self.task_dir = os.path.join(os.path.dirname(self.project_root), "examples", "operational_tasks")')
p.write_text(source, encoding='utf-8')

# Restrict solid server execution to its own station and current interpreter.
p = SOLID / 'server/station_server.py'
source = p.read_text(encoding='utf-8').split('if __name__ == "__main__":')[0]
source = source.replace('import subprocess', 'import subprocess\nimport sys\nfrom pathlib import Path\nfrom io import StringIO')
source = source.replace('pd.read_json(df_json, orient="split")', 'pd.read_json(StringIO(df_json), orient="split")')
source = source.replace('command_parts, capture_output=True, text=True', '[sys.executable, str(Path(__file__).resolve().parents[1] / "main.py"), *command_parts[2:]],\n                capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1]')
p.write_text(source, encoding='utf-8')

# Strip empty translated comments and obsolete commented code in solid modules.
for p in SOLID.rglob('*.py'):
    source = p.read_text(encoding='utf-8')
    source = re.sub(r'^\s*#.*(?:breakpoint\(|logger\.|self\.|motion\.|solid_weigh\.| = |if |for |try:|except |continue|return |Args:|Returns:|"""|def ).*\n', '', source, flags=re.M)
    p.write_text(source, encoding='utf-8')
print('Refactored station initialization, CLI, calibrated calls, example paths, and vendor loading.')
