# Solid Handling Station

## Notice on Code Availability

The solid handling station is part of the overall automated photocatalysis platform described in this repository. It is responsible for solid reagent handling and related station-level operations within the multi-station workflow.

However, the source code for this module is not included in the public or supplementary release of the repository.

## Reason for Omission

The solid handling station code cannot be openly released because of conflict-of-interest constraints associated with the implementation, ownership, and surrounding collaboration context of this part of the system.

To avoid disclosing code that cannot be shared appropriately, this directory is intentionally limited to documentation only.

## What Is Still Reflected in This Repository

Although the station-specific implementation is not provided here, the rest of the repository still contains references that show how the solid handling station fits into the full automation architecture, including:

- task splitting logic in the automation control hub
- status and inventory tracking entries related to the solid station
- client/server communication hooks used by other modules
- workflow-level references showing where solid-handling steps occur

These retained references are included to preserve the completeness of the system description and the end-to-end workflow context used in the project.

## Scope of This Placeholder Directory

This folder is a placeholder to indicate that:

- a solid handling station exists in the original platform
- it participates in the full automated workflow
- its code is intentionally unavailable in this release

## For Readers and Reviewers

This omission does not mean the station was absent from the original automation platform. Rather, it reflects a documentation boundary for this release.

Where possible, the surrounding repository has been kept informative enough to show:

- how the control hub expects to interact with the solid station
- where solid-handling tasks appear in the workflow
- how the solid station relates to the other published modules

If a higher level architectural explanation is needed, refer to the repository-level documentation:

- [`README.md`](../README.md)
- [`SYSTEM_ARCHITECTURE.md`](../SYSTEM_ARCHITECTURE.md)
- [`REPRODUCE.md`](../REPRODUCE.md)
