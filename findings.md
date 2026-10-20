# Findings

- The initial README incorrectly states that solid station code is absent; the user has supplied an untracked solid_handling_station directory.
- Representative task workbooks exist on disk but were hidden by blanket task-directory ignore rules; explicitly include them in the release.
- Python caches, hundreds of operational logs, duplicated scripts, and vendor DLLs are present.
- pyproject.toml declares no dependencies and targets Python 3.10 only; a separate requirements file is unpinned.
- Target journal is unspecified; optional clarification requested.
- Nature's official GuidelinesCodePublication.pdf requests versioned source, installation/platform/dependency documentation, example data/demo and runtime, license terms, and maintained identifiers.
- All 50 baseline tests passed on CPython 3.10.19 / Windows x64 in an isolated environment.
- A hardcoded mail credential exists in an unused solid station utility; exclude it from the release. User informed that revocation is necessary. Do not record the credential in notes.
- Full initial files, excluding Git and the new virtual environment, are preserved in a sibling local backup ZIP. This private backup must not be uploaded.
- Bulk removal of 272 reviewed files was rejected by automatic review. No original files were deleted. The new publication_release directory excludes these files and historical task output, retaining six representative task inputs.
- Active solid code has import-time logging/workbook reads, duplicate method definitions, calibration calls missing required arguments, and CLI parsing after device initialization.
- The independent release now fixes those issues, preserves the drive commands/coarse-fine strategy, and includes pure task validation, explicit runtime assembly, checkpointed measured outputs and mock control tests.
- All 67 current tests pass: hub 17, liquid 8, mobile 10, reactor 17, solid 11, root 4. Demo output matches its supplied deterministic reference.
- ZMotion library loading is lazy with a configurable absolute path, separate supplier installation and explicit third-party rights notes.
- Hub legacy transfer commands do not match the supplied mobile subcommand CLI; solid rack-transfer operations are also absent. These gaps are documented rather than invented.
- Existing restrictive LICENSE is retained. Authors, journal, DOI, manuscript/result mappings, vendor-wrapper/UI icon rights and hardware validation remain author-supplied fields, explicitly recorded in English documentation.
