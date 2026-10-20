"""Audit the upload payload without importing hardware drivers."""

import ast
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".vscode",
    ".idea",
    "dist",
    "build",
    "logs",
    "log",
    "task",
    "tasks",
    "model",
    "outputs",
    ".publication-work",
}
LOCAL_FILES = {"task_plan.md", "findings.md", "progress.md", "MANIFEST.sha256"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".ui", ".xml", ".cff"}
FORBIDDEN_SUFFIXES = {".log", ".pyc", ".pyo", ".dll", ".pkl", ".zip"}
CJK = re.compile(r"[\u3400-\u9fff]")


def release_files(root=ROOT):
    root = Path(root)
    files = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        relative = p.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts) or p.name in LOCAL_FILES:
            continue
        files.append(p)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def audit(root=ROOT):
    root = Path(root)
    issues = []
    files = release_files(root)
    for p in files:
        relative = p.relative_to(root).as_posix()
        if CJK.search(relative):
            issues.append(f"Non-English path: {relative}")
        if p.suffix.lower() in FORBIDDEN_SUFFIXES:
            issues.append(f"Non-release artifact: {relative}")
        if p.is_symlink():
            issues.append(f"Symbolic link requires explicit review: {relative}")
        if p.suffix.lower() in TEXT_SUFFIXES or p.name in {
            "LICENSE",
            ".gitignore",
            ".python-version",
        }:
            source = p.read_text(encoding="utf-8-sig")
            if CJK.search(source):
                issues.append(f"Chinese text remains: {relative}")
            if re.search(r"(?:[A-Za-z]:[\\/]+Users[\\/])", source):
                issues.append(f"Personal absolute path: {relative}")
            if p.suffix == ".py":
                try:
                    tree = ast.parse(source, filename=relative)
                    for n in ast.walk(tree):
                        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant):
                            if isinstance(n.value.value, str) and n.value.value:
                                if any(
                                    isinstance(t, ast.Name)
                                    and t.id.lower()
                                    in {
                                        "password",
                                        "passwd",
                                        "api_key",
                                        "access_token",
                                        "secret_key",
                                    }
                                    for t in n.targets
                                ):
                                    issues.append(
                                        f"Potential embedded credential: {relative}:{n.lineno}"
                                    )
                except SyntaxError as exc:
                    issues.append(f"Python syntax error: {relative}:{exc.lineno}")
        if p.suffix == ".xlsx":
            try:
                with zipfile.ZipFile(p) as z:
                    if z.testzip():
                        issues.append(f"Corrupt workbook: {relative}")
                    for name in z.namelist():
                        if name.endswith(".xml") and CJK.search(z.read(name).decode("utf-8")):
                            issues.append(f"Chinese workbook text: {relative}:{name}")
            except zipfile.BadZipFile:
                issues.append(f"Invalid workbook: {relative}")
    return {"file_count": len(files), "issues": sorted(set(issues))}


def manifest(root=ROOT):
    root = Path(root)
    return "".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}\n"
        for p in release_files(root)
    )


def main():
    result = audit()
    print(json.dumps(result, indent=2))
    return int(bool(result["issues"]))


if __name__ == "__main__":
    raise SystemExit(main())
