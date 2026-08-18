# DAPHNE interface data

Status: **proposed revision 8 review input — not an approved operational
configuration**.

This directory records the DAPHNE variable-intake workbook used to review the
PDS–DAQ and PDS–Slow Controls interface boundary. It contains 383 variable
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
- `exports/` — one stable CSV file per worksheet for code review and comparison,
  including the structured `np02_compatibility.csv` transcription and the
  generated `protobuf_field_trace.csv` wire-field ledger.
- `manifest.yaml` — status, scope, provenance, counts, and known gaps.
- `SHA256SUMS` — integrity hashes for the workbook, policy, and CSV exports.
- `nodeset/` — location reserved for the approved project-specific NodeSet XML.
- `scripts/export_workbook.py` — deterministic export and consistency checker.

## NP02 compatibility evidence

The `NP02 Compatibility` worksheet transcribes the supplied one-page
`NP02interlockMatrix.pdf`, created 10 March 2025. The source matrix is symmetric
and classifies all 15 unique pairings among PoF, LEDs, PMTs, PDs, IoL, and PrM:
six incompatible, five compatible, and four probably compatible.

This is historical NP02 admission evidence, not a production cause-and-effect
specification:

- **Incompatible** supports blocking a newly requested activation while its
  peer is active. It does not identify which already-active system must trip.
- **Compatible** removes only that pairwise exclusion; other permits and state
  guards remain applicable.
- **Probably compatible** remains unresolved and must not be accepted as an
  automatic operating permit.

The source does not identify an author or controlled document revision, define
the scope of “LEDs,” or provide signal paths, quality/freshness, detector-region
mapping, timing, priority, failure response, recovery, or approval. In
particular, its PDs–PrM orange cell conflicts with SC–PDS ICD draft v1, which
requires PDS SiPM bias off while the Purity Monitor is active. Its LEDs–PDs red
cell supports the intended camera-LED exclusion, while PDs–IoL identifies an
ionisation-laser constraint missing from that draft. These points require owner
resolution before production use.

The working expansion of IoL as the ionisation-laser system is supported by the
[official NP02 activity update of 26 February 2025](https://indico.cern.ch/event/1522253/contributions/6404491/attachments/3026376/5341354/TB_Feb25.pdf),
which provides context but does not approve the compatibility classifications.

The PDF is not redistributed in this repository. Its exact SHA-256 digest and
limitations are recorded in `manifest.yaml` and the workbook's `Source Audit`
sheet.

## Explicit Protobuf trace

`exports/protobuf_field_trace.csv` is the reviewable field-number ledger for
the proposed v8 DAPHNE telemetry schema. It maps each of the 316 board-owned
variable patterns to one named `BoardTelemetry` field, its stable field number,
typed sample or repeated instance wrapper, explicit instance keys, OPC-UA
NodeId pattern, engineering unit, data source, and control owner. Those fields
expand to 1,370 samples for the current HD board instance set.

The `field_status` column preserves retired entries. Their numbers and names
remain reserved in the generated schema, so removing a variable cannot make a
later variable silently reuse its wire identity.

The canonical generator and schema live in `daphneZMQ` at
`scripts/generate_v8_explicit_proto.py` and
`srcs/protobuf/daphne_v8_telemetry.proto`. The copy compiled by `daphne-sc`
must be byte-for-byte identical. The bridge consumes the compiled field
declarations; it is not the owner of a parallel mapping table.

The schema defines a complete read-snapshot request/response. DAQ configuration
messages remain in the DAQ-owned high-level protobuf and `daphnemodules`.
Monitoring a DAQ-owned setting through this snapshot does not transfer write
authority to Slow Controls.

## Refresh and verify

From the repository root, regenerate all workbook CSV exports, verify the
explicit Protobuf trace, and refresh checksums with:

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
