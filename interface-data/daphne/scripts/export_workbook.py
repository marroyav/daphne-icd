#!/usr/bin/env python3
"""Export the DAPHNE intake workbook to stable CSV files and verify drift."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
import unicodedata
from datetime import date, datetime, time
from pathlib import Path

from openpyxl import load_workbook


DAPHNE_DIR = Path(__file__).resolve().parents[1]
WORKBOOK = DAPHNE_DIR / "DAPHNE_DCS_Full_Variable_Intake.xlsx"
POLICY = DAPHNE_DIR / "DAPHNE_OPCUA_Control_Policy.csv"
EXPORT_DIR = DAPHNE_DIR / "exports"
CHECKSUMS = DAPHNE_DIR / "SHA256SUMS"
POLICY_SHEET = "OPC-UA Control Policy"


def render(value: object) -> str:
    """Return a stable, human-readable CSV representation of an Excel value."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, str):
        return value.replace("\r\n", "\n").replace("\r", "\n").rstrip()
    return str(value)


def filename_for_sheet(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")
    if not slug:
        raise ValueError(f"worksheet name has no usable filename: {title!r}")
    return f"{slug}.csv"


def export_bytes() -> dict[str, bytes]:
    workbook = load_workbook(WORKBOOK, read_only=True, data_only=False)
    outputs: dict[str, bytes] = {}
    try:
        for worksheet in workbook.worksheets:
            buffer = io.StringIO(newline="")
            writer = csv.writer(buffer, lineterminator="\n")
            for row in worksheet.iter_rows():
                writer.writerow([render(cell.value) for cell in row])
            name = filename_for_sheet(worksheet.title)
            if name in outputs:
                raise ValueError(f"worksheet filename collision: {name}")
            outputs[name] = buffer.getvalue().encode("utf-8")
    finally:
        workbook.close()
    return outputs


def checksum_bytes(exports: dict[str, bytes]) -> bytes:
    artifacts: dict[str, bytes] = {
        WORKBOOK.name: WORKBOOK.read_bytes(),
        POLICY.name: exports[filename_for_sheet(POLICY_SHEET)],
    }
    artifacts.update({f"exports/{name}": data for name, data in exports.items()})
    lines = [
        f"{hashlib.sha256(data).hexdigest()}  {name}\n"
        for name, data in sorted(artifacts.items())
    ]
    return "".join(lines).encode("ascii")


def update() -> None:
    exports = export_bytes()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for name, data in exports.items():
        (EXPORT_DIR / name).write_bytes(data)
    POLICY.write_bytes(exports[filename_for_sheet(POLICY_SHEET)])
    CHECKSUMS.write_bytes(checksum_bytes(exports))
    print(f"exported {len(exports)} worksheets and refreshed {CHECKSUMS.name}")


def check() -> int:
    exports = export_bytes()
    problems: list[str] = []
    expected_names = set(exports)
    actual_names = {path.name for path in EXPORT_DIR.glob("*.csv")}

    for name in sorted(expected_names - actual_names):
        problems.append(f"missing export: exports/{name}")
    for name in sorted(actual_names - expected_names):
        problems.append(f"unexpected export: exports/{name}")
    for name in sorted(expected_names & actual_names):
        if (EXPORT_DIR / name).read_bytes() != exports[name]:
            problems.append(f"stale export: exports/{name}")

    policy_data = exports[filename_for_sheet(POLICY_SHEET)]
    if not POLICY.exists() or POLICY.read_bytes() != policy_data:
        problems.append(f"stale policy export: {POLICY.name}")

    expected_checksums = checksum_bytes(exports)
    if not CHECKSUMS.exists() or CHECKSUMS.read_bytes() != expected_checksums:
        problems.append(f"stale integrity file: {CHECKSUMS.name}")

    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1

    print(f"verified {len(exports)} worksheet exports, policy, and checksums")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift without rewriting generated files",
    )
    args = parser.parse_args()
    if not WORKBOOK.is_file():
        parser.error(f"workbook not found: {WORKBOOK}")
    return check() if args.check else (update() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
