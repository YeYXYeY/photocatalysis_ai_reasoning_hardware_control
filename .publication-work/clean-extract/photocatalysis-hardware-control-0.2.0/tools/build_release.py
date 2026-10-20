"""Build a deterministic, audited ZIP with file and archive SHA-256 checksums."""

import argparse
import hashlib
from pathlib import Path
import zipfile

from tools.validate_release import ROOT, audit, manifest, release_files

VERSION = "0.2.0"
ARCHIVE_ROOT = f"photocatalysis-hardware-control-{VERSION}"


def build(output_dir):
    report = audit()
    if report["issues"]:
        raise ValueError("Release audit failed: " + "; ".join(report["issues"]))
    output_dir = Path(output_dir).resolve()
    if output_dir == ROOT or ROOT in output_dir.parents and output_dir != ROOT / "dist":
        raise ValueError("Use dist/ or an output directory outside the release source tree.")
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{ARCHIVE_ROOT}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in release_files():
            info = zipfile.ZipInfo(
                f"{ARCHIVE_ROOT}/{p.relative_to(ROOT).as_posix()}", (2026, 10, 20, 0, 0, 0)
            )
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
        info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/MANIFEST.sha256", (2026, 10, 20, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        z.writestr(info, manifest().encode("utf-8"))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise RuntimeError("Archive integrity verification failed.")
    print(f"{archive}\nSHA256 {digest}")
    return archive


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args(argv)
    build(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
