# Publication preparation status

## Included and executable

Versioned source for the supplied five-module codebase; English source text and documentation; exact dependency pins; full Windows environment lock; a hardware-free demo with explicit synthetic inputs and expected output; isolated tests; documented data schemas and hardware prerequisites; automated release audit; reproducible ZIP packaging and SHA-256 manifests. Validation results are recorded in `VALIDATION_REPORT.md`.

## Author information still needed

1. Enter the exact author list, corresponding contact, manuscript title, target journal/article type, repository URL, and persistent archive identifier in `release_metadata.json`. Submit any journal-specific software checklist.
2. Confirm the existing restrictive LICENSE is the intended release license and meets the selected journal's access terms. Any switch to another license requires the copyright holders' decision. Confirm vendor-wrapper and UI asset provenance/redistribution terms.
3. Map manuscript figures/results to exact scripts, parameters and supporting datasets, and identify the version used for the reported experiments. The supplied material does not include a complete manuscript/AI reasoning/figure-data reproduction pipeline.
4. Record and validate hardware/firmware/SDK versions, robot-side programs, AGV maps, operational task units, calibration, interlocks, and missing command adapters in `HARDWARE.md`. Independent laboratory validation remains required for an end-to-end physical claim.
5. Revoke or rotate the mail credential discovered in the original local source. It is absent from this release; the original working directory and private local backup still contain the original material and must not be uploaded.

A source archive can be uploaded as prepared supplementary software, with these limits disclosed. This preparation does not certify journal acceptance, open-source compliance, unprovided data rights, or experimental reproducibility.
