# Changes in 0.2.0

## Publication structure

Included the supplied solid station alongside the four existing hub/station directories; corrected the outdated documentation-only placeholder claim. Kept station process boundaries to preserve local package imports. Added root demo/test/audit/package commands, dependency pins, a complete Windows lock file, English documentation, reference demo output and an upload manifest.

## Solid station

Separated task validation, file/log setup and workflow execution into `app/`. Moved device/workbook/log initialization out of import paths, made CLI parsing precede device setup, retained checkpointed measured masses, removed a shadowed duplicate `weighing_params` definition, fixed missing `align_pos` arguments to calibration calls, and replaced the literal `{current_time}` output-name bug with a run-specific directory and `actual_weight.xlsx`. Reusable regression calibration now loads its files explicitly, uses portable paths and supports an optional seed; its default stochastic behavior remains available.

The dispensing thresholds, drive command values, motion sequence, and core coarse/fine strategy were retained. These changes have software-level regression coverage and have not been validated against physical equipment.

## Cleanup and portability

Translated non-English runtime messages/docstrings, retained useful English comments and removed redundant comments/debug examples. Removed unused legacy copies/prototypes and mail utilities from the release payload. Excluded historical logs/cache/editor state/task outputs and vendor DLLs. Replaced the hardcoded supplier DLL path with a lazy loader and `ZMOTION_LIBRARY` override. Moved retained operational task inputs into `examples/operational_tasks/`. Normalized Office document properties and Chinese font/style names without changing cells/formulas. The original working directory and a private backup remain local.

## Remaining boundaries

The original integration gaps, rights questions, unprovided manuscript metadata and missing scientific data are explicitly described in the publication checklist and hardware notes. This preparation does not convert the supplied code into a fully integrated physical deployment or fabricate missing experiments/programs.
