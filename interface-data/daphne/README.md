# DAPHNE interface data

Status: **proposed revision 8 review input — not an approved operational
configuration**.

This directory records the DAPHNE variable-intake workbook used to review the
PDS–DAQ and PDS–Slow Controls interface boundary. It contains 379 variable
patterns and 21 proposed or existing OPC-UA operations. The workbook separates
current implementations, locally readable values, required production work,
expert-only operations, and items excluded from routine Slow Controls.

No alarm threshold, interlock limit, endpoint assignment, or final permission
policy should be inferred merely from the presence of a row in this workbook.

## Authority boundary

| Subject | Authoritative owner or source |
| --- | --- |
| Configuration that determines acquired data | DAQ, with the configuration source maintained in the DUNE-DAQ framework and `daphnemodules` |
| Equipment lifecycle, power, availability, health monitoring, protection, and safe-state actions | Slow Controls, subject to the approved SC configuration and DPS authority |
| Shared paths, types, roles, mappings, state guards, and command semantics | The jointly approved interface artifacts, including the project-specific OPC-UA NodeSet and mapping |

Monitoring or archiving a value does not confer permission to write it. The
workbook is an interface intake and review artifact, not an executable runtime
configuration and not an independent Slow Controls copy of the DAQ schema.

## Contents

- `DAPHNE_DCS_Full_Variable_Intake.xlsx` — human-oriented intake workbook.
- `DAPHNE_OPCUA_Control_Policy.csv` — machine-readable export of the workbook's
  OPC-UA control-policy sheet.
- `exports/` — one stable CSV file per worksheet for code review and comparison.
- `manifest.yaml` — status, scope, provenance, counts, and known gaps.
- `SHA256SUMS` — integrity hashes for the workbook, policy, and CSV exports.
- `nodeset/` — location reserved for the approved project-specific NodeSet XML.
- `scripts/export_workbook.py` — deterministic export and consistency checker.

## Refresh and verify

From the repository root, regenerate all CSV exports and checksums with:

```sh
uv run --with openpyxl python interface-data/daphne/scripts/export_workbook.py
```

Check that the tracked exports still match the workbook without changing files:

```sh
uv run --with openpyxl python interface-data/daphne/scripts/export_workbook.py --check
```

The standard checksum utility can also verify the artifact set:

```sh
cd interface-data/daphne
sha256sum --check SHA256SUMS
```

When the workbook changes, reviewers should inspect the generated CSV diff,
update the version/status metadata in `manifest.yaml`, and identify the
approvals and ICD requirements affected. The binary workbook must never be the
only reviewable representation of a proposed interface change.
