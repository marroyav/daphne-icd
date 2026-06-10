# PDS–DAQ ICD Package

This folder contains a LaTeX project that builds an ICD for the PDS–DAQ interface.

## Build

Use `latexmk` (recommended):

```
latexmk -pdf main.tex
```

## Structure

- `main.tex` — entry point (cernatlasnote class)
- `includes/requirements.tex` — interface requirements & budgets
- `includes/timing.tex` — timing and synchronization
- `includes/data_formats.tex` — packetization and frame layout (includes generated tables)
- `includes/ccm.tex` — control, configuration, and monitoring
- `includes/operations.tex` — commissioning & fault handling
- `includes/compat.tex` — compatibility, dependencies, security
- `includes/vv.tex` — verification & validation plan
- `includes/missing.tex` — outstanding items checklist
- `includes/acronyms.tex` — glossary entries
- `tables/header_longtable.tex` — header field table (auto-generated from Excel)
- `tables/payload_longtable.tex` — payload field table (auto-generated from Excel)
- `tables/frame_decoder_map.csv` — machine-readable decoder map

## Notes

- The header/payload tables are programmatically derived from: `DAPHNE-DAQ_Format_Ethernet_25_09_25.xlsx` (sheet: "Simple Self-trigger").
- Update the Excel and rerun the conversion to refresh the tables and CSV.
