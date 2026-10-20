# Publication preparation

## Objective
Prepare a complete English-language research software release, with documented installation, a safe software-only demonstration, tests, data provenance, and an upload archive.

## Phases
1. Audit files, existing changes, dependencies, hardware boundaries, and publication requirements. (complete)
2. Translate retained content and improve configuration, structure, and documentation. (complete)
3. Validate software without operating connected hardware; address failures. (complete)
4. Exclude unnecessary release artifacts and build a verified upload archive. (complete)

## Decisions
- Preserve the initial uncommitted deletion of solid-handling-station/README.md and the newly supplied solid_handling_station implementation.
- Do not execute physical hardware workflows during validation.
- Keep experimental records recoverable; delete only verified disposable files.
- Never invent publication metadata, scientific results, hardware validation, or third-party redistribution permissions.
- Automatic review rejected bulk deletion. Build publication_release non-destructively and preserve original files; do not retry the deletion.

## Errors
- Initial shell inventory returned exit code 1 because some optional commands were absent; inspect Python separately.
- First hub baseline command used an incorrect interpreter path; corrected it, then all 17 hub tests passed.
- The uv-created environment has no pip module; generated its exact lock with uv pip freeze instead.
- Extended duplicate-name lint found a redundant datetime import in a retained alternate liquid helper. Ruff did not auto-fix it; inspected the only use (datetime.datetime) and removed the shadowed class import manually.
