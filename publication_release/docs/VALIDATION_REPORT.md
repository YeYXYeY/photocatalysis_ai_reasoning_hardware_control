# Validation report

Preparation date: 2026-10-20. Release version: 0.2.0.

## Measured environment and commands

Windows x64, CPython 3.10.19. Dependencies were installed in an isolated virtual environment; exact versions are in `../requirements-lock-windows.txt`. No physical hardware run was performed.

| Command | Exit status | Measured wall time (s) |
| --- | --- | --- |
| `python main.py demo` | 0 | 0.676 |
| `python main.py test` | 0 | 5.280 |
| `python main.py check` | 0 | 0.358 |
| `python -m ruff check .` | 0 | 0.118 |
| `python -m ruff format --check .` | 0 | 0.133 |

Timings are observations on the preparation machine and include interpreter startup. They vary with storage, package caches and CPU load. Demo output exactly matches `../examples/expected_demo_output.json`.

## Regression coverage

67 test methods passed: hub 17, liquid 8, mobile 10, reactor 17, solid 11, release/root 4. The inherited baseline comprised 50 passing tests; 17 tests were added for solid validation/mock workflow/calibration, vendor loading, safe CLI help, demo and release rules. Device interactions are mocked; station `--help` commands run in separate processes without device construction.

Ruff's configured checks cover fatal syntax/name issues and duplicate definitions; formatting is checked separately. Passing these selected checks is not a claim of exhaustive static or hardware verification.

## Workbook preservation and release audit

33 retained XLSX workbooks were compared with their original files. All workbook member names and all non-document-property/style/theme member bytes match the source. Cell values/formulas and sheet XML are unchanged. Differences are limited to normalized Office properties and Chinese font/style names. Original/release SHA-256 values, changed members and table headers are in `WORKBOOK_INVENTORY.json`.

The release payload audit reports no detected Chinese source/workbook XML text, personal absolute user paths, literal credentials or disallowed runtime/binary artifacts. `EXCLUDED_FILES.json` records 323 original files excluded from publication; all remain in the original local directory/private backup. No experimental relevance was inferred for excluded measurement histories.

## Clean-extraction verification

The prepared ZIP was extracted into a new directory outside the release source tree. A second fresh CPython 3.10.19 virtual environment was populated only from the archived Windows lock file. All 267 payload-file hashes matched the manifest. All 67 tests, the exact-output demo, release audit and static/format checks passed from the extracted copy.

| Extracted-copy command | Exit status | Measured wall time (s) |
| --- | --- | --- |
| `python main.py demo` | 0 | 2.251 |
| `python main.py test` | 0 | 9.640 |
| `python main.py check` | 0 | 0.414 |
| `python -m ruff check .` | 0 | 0.283 |
| `python -m ruff format --check .` | 0 | 0.195 |

After this verification, only this report was updated to record the result. The final archive was rebuilt; the source, inputs, lock file, tests and tools were compared with the tested archive, and the final manifest was verified again. CI configuration is supplied for future Windows/Python 3.10 runs; no remote CI run is claimed.

## Limits

No manuscript/figure pipeline, full experimental dataset, AI reasoning/model component, robot-side programs, AGV maps or validated cross-station command adapters were supplied. Physical timing, collision/interlock behavior, chemical performance, end-to-end station coordination and third-party publication rights are not established by these tests. See `HARDWARE.md` and `PUBLICATION_CHECKLIST.md`.
