#!/usr/bin/env python3
"""Check that the 1NF CSV files still contain the original data.

Run from anywhere:

    python3 1NF/validate_1nf.py
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NF_DIR = Path(__file__).resolve().parent
ORIGINAL_PATH = ROOT / "construction_projects.csv"

ORIGINAL_COLUMNS = [
    "ProjectID",
    "ProjectName",
    "ProjectType",
    "StartDate",
    "EndDate",
    "SiteAddress",
    "SiteCity",
    "SiteState",
    "ClientName",
    "ClientPhone",
    "ClientEmail",
    "ClientCity",
    "SupervisorName",
    "SupervisorPhone",
    "WorkerName",
    "WorkerPhone",
    "WorkerSkills",
    "WorkerCertifications",
    "WorkerHourlyRate",
    "SupplierName",
    "SupplierCity",
    "SupplierPhones",
    "MaterialSupplied",
    "MaterialUnitCost",
    "EquipmentUsed",
    "EquipmentRentalCost",
]

# Columns that were already one value per cell in the original file.
SINGLE_VALUE_COLUMNS = [
    "ProjectID",
    "ProjectName",
    "ProjectType",
    "StartDate",
    "EndDate",
    "SiteAddress",
    "SiteCity",
    "SiteState",
    "ClientName",
    "ClientPhone",
    "ClientEmail",
    "ClientCity",
    "SupervisorName",
    "SupervisorPhone",
    "WorkerName",
    "WorkerPhone",
    "WorkerHourlyRate",
    "SupplierName",
    "SupplierCity",
]

EXPECTED_HEADERS = {
    "project_assignments_1nf.csv": SINGLE_VALUE_COLUMNS,
    "worker_skills_1nf.csv": ["ProjectID", "WorkerName", "WorkerPhone", "WorkerSkill"],
    "worker_certifications_1nf.csv": [
        "ProjectID",
        "WorkerName",
        "WorkerPhone",
        "WorkerCertification",
    ],
    "supplier_phones_1nf.csv": ["ProjectID", "SupplierName", "SupplierPhone"],
    "materials_1nf.csv": [
        "ProjectID",
        "SupplierName",
        "MaterialSupplied",
        "MaterialUnitCost",
    ],
    "equipment_1nf.csv": [
        "ProjectID",
        "SupplierName",
        "EquipmentUsed",
        "EquipmentRentalCost",
    ],
}

KEYS = {
    "project_assignments_1nf.csv": ["ProjectID", "WorkerPhone"],
    "worker_skills_1nf.csv": ["ProjectID", "WorkerPhone", "WorkerSkill"],
    "worker_certifications_1nf.csv": ["ProjectID", "WorkerPhone", "WorkerCertification"],
    "supplier_phones_1nf.csv": ["ProjectID", "SupplierName", "SupplierPhone"],
    "materials_1nf.csv": ["ProjectID", "SupplierName", "MaterialSupplied"],
    "equipment_1nf.csv": ["ProjectID", "SupplierName", "EquipmentUsed"],
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.name} is empty")
    header, data = rows[0], rows[1:]
    if any(cell.strip() == "" for cell in header):
        raise ValueError(f"{path.name} has a blank column header")
    if len(header) != len(set(header)):
        raise ValueError(f"{path.name} has a repeated column header: {header}")
    for line_no, row in enumerate(data, 2):
        if len(row) != len(header):
            raise ValueError(
                f"{path.name} line {line_no} has {len(row)} cells, expected {len(header)}"
            )
        if any(cell.strip() == "" for cell in row):
            raise ValueError(f"{path.name} line {line_no} has an empty cell")
    return header, [dict(zip(header, row)) for row in data]


def split_list(cell):
    parts = [part.strip() for part in cell.split("|")]
    if any(part == "" for part in parts):
        raise ValueError(f"Blank item inside list: {cell!r}")
    return parts


def key_of(row, columns):
    return tuple(row[column] for column in columns)


def check_unique(file_name, rows):
    columns = KEYS[file_name]
    seen = set()
    for row in rows:
        key = key_of(row, columns)
        if key in seen:
            raise ValueError(f"{file_name} repeats key {key}")
        seen.add(key)


def check_no_pipes(file_name, rows):
    for row in rows:
        for column, value in row.items():
            if "|" in value:
                raise ValueError(f"{file_name} still has a list in {column}: {value}")


def grouped_values(rows, key_columns, value_column):
    grouped = {}
    for row in rows:
        key = key_of(row, key_columns)
        grouped.setdefault(key, []).append(row[value_column])
    return grouped


def main():
    failures = []

    def check(name, test):
        try:
            detail = test()
        except Exception as error:  # noqa: BLE001 - report every failed check
            failures.append(f"FAIL {name}: {error}")
            print(f"FAIL {name}: {error}")
            return
        print(f"PASS {name}" + (f" — {detail}" if detail else ""))

    original_header, original = read_csv(ORIGINAL_PATH)
    if original_header != ORIGINAL_COLUMNS:
        raise ValueError(f"original headers are {original_header}")
    tables = {}
    for file_name in EXPECTED_HEADERS:
        header, rows = read_csv(NF_DIR / file_name)
        tables[file_name] = rows
        if header != EXPECTED_HEADERS[file_name]:
            raise ValueError(f"{file_name} headers are {header}")

    check(
        "original file opens",
        lambda: f"{len(original)} data rows, {len(original_header)} columns",
    )
    check(
        "1NF files open with the expected headers",
        lambda: f"{len(tables)} files",
    )

    def no_pipes():
        for file_name, rows in tables.items():
            check_no_pipes(file_name, rows)
        return "no cell contains |"

    check("every 1NF cell is a single value", no_pipes)

    def unique_keys():
        counts = []
        for file_name, rows in tables.items():
            check_unique(file_name, rows)
            counts.append(f"{file_name} {len(rows)}")
        return "; ".join(counts)

    check("proposed keys are unique", unique_keys)

    def single_values_match():
        assignments = {
            key_of(row, ["ProjectID", "WorkerPhone"]): row
            for row in tables["project_assignments_1nf.csv"]
        }
        if len(assignments) != len(original):
            raise ValueError("assignment row count does not match the original")
        for source in original:
            for column in SINGLE_VALUE_COLUMNS:
                if "|" in source[column]:
                    raise ValueError(f"{column} still has a list in the original file")
            key = key_of(source, ["ProjectID", "WorkerPhone"])
            if key not in assignments:
                raise ValueError(f"missing assignment row {key}")
            for column in SINGLE_VALUE_COLUMNS:
                if assignments[key][column] != source[column]:
                    raise ValueError(
                        f"{key} {column}: {assignments[key][column]!r} != {source[column]!r}"
                    )
        return f"{len(original)} assignment rows match"

    check("single-value columns match the original rows", single_values_match)

    def skills_match():
        found = grouped_values(
            tables["worker_skills_1nf.csv"],
            ["ProjectID", "WorkerPhone"],
            "WorkerSkill",
        )
        for source in original:
            key = key_of(source, ["ProjectID", "WorkerPhone"])
            expected = split_list(source["WorkerSkills"])
            if found.get(key) != expected:
                raise ValueError(f"{key}: {found.get(key)} != {expected}")
        actual = sum(len(values) for values in found.values())
        expected_count = sum(len(split_list(row["WorkerSkills"])) for row in original)
        if actual != expected_count:
            raise ValueError("skill row count is not the number of original skill values")
        return f"{actual} skills, same order as the original cells"

    check("worker skills match and were not crossed with other lists", skills_match)

    def certs_match():
        found = grouped_values(
            tables["worker_certifications_1nf.csv"],
            ["ProjectID", "WorkerPhone"],
            "WorkerCertification",
        )
        for source in original:
            key = key_of(source, ["ProjectID", "WorkerPhone"])
            expected = split_list(source["WorkerCertifications"])
            if found.get(key) != expected:
                raise ValueError(f"{key}: {found.get(key)} != {expected}")
        actual = sum(len(values) for values in found.values())
        return f"{actual} certifications"

    check("worker certifications match and stay separate from skills", certs_match)

    def names_match():
        assignment_names = {}
        for row in tables["project_assignments_1nf.csv"]:
            phone = row["WorkerPhone"]
            name = row["WorkerName"]
            if phone in assignment_names and assignment_names[phone] != name:
                raise ValueError(f"{phone} is used by more than one worker name")
            assignment_names[phone] = name
        for file_name in ("worker_skills_1nf.csv", "worker_certifications_1nf.csv"):
            for row in tables[file_name]:
                if assignment_names[row["WorkerPhone"]] != row["WorkerName"]:
                    raise ValueError(f"{file_name} name does not match {row['WorkerPhone']}")
        return "worker names agree with the assignment table"

    check("worker names on the child tables are the original names", names_match)

    def phones_match():
        found = grouped_values(
            tables["supplier_phones_1nf.csv"],
            ["ProjectID", "SupplierName"],
            "SupplierPhone",
        )
        for source in original:
            key = (source["ProjectID"], source["SupplierName"])
            expected = split_list(source["SupplierPhones"])
            if found.get(key) != expected:
                raise ValueError(f"{key}: {found.get(key)} != {expected}")
        if len(tables["supplier_phones_1nf.csv"]) != sum(len(v) for v in found.values()):
            raise ValueError("unexpected extra phone rows")
        return f"{len(tables['supplier_phones_1nf.csv'])} phone rows"

    check("supplier phones match each project and supplier", phones_match)

    def paired_match(file_name, item_column, cost_column, source_items, source_costs):
        found = {}
        for row in tables[file_name]:
            key = (row["ProjectID"], row["SupplierName"])
            found.setdefault(key, []).append((row[item_column], row[cost_column]))
        for source in original:
            key = (source["ProjectID"], source["SupplierName"])
            items = split_list(source[source_items])
            costs = split_list(source[source_costs])
            if len(items) != len(costs):
                raise ValueError(f"{key}: {source_items} and {source_costs} have different lengths")
            expected = list(zip(items, costs))
            if found.get(key) != expected:
                raise ValueError(f"{key}: {found.get(key)} != {expected}")
        return len(tables[file_name])

    check(
        "materials stay paired with the cost in the same position",
        lambda: (
            f"{paired_match('materials_1nf.csv', 'MaterialSupplied', 'MaterialUnitCost', 'MaterialSupplied', 'MaterialUnitCost')} material rows"
        ),
    )
    check(
        "equipment stays paired with the rental cost in the same position",
        lambda: (
            f"{paired_match('equipment_1nf.csv', 'EquipmentUsed', 'EquipmentRentalCost', 'EquipmentUsed', 'EquipmentRentalCost')} equipment rows"
        ),
    )

    def no_extra_children():
        assignment_keys = {
            key_of(row, ["ProjectID", "WorkerPhone"])
            for row in tables["project_assignments_1nf.csv"]
        }
        supplier_keys = {
            (row["ProjectID"], row["SupplierName"])
            for row in tables["project_assignments_1nf.csv"]
        }
        for file_name in ("worker_skills_1nf.csv", "worker_certifications_1nf.csv"):
            for row in tables[file_name]:
                if key_of(row, ["ProjectID", "WorkerPhone"]) not in assignment_keys:
                    raise ValueError(f"{file_name} has an unknown worker {row}")
        for file_name in (
            "supplier_phones_1nf.csv",
            "materials_1nf.csv",
            "equipment_1nf.csv",
        ):
            for row in tables[file_name]:
                if (row["ProjectID"], row["SupplierName"]) not in supplier_keys:
                    raise ValueError(f"{file_name} has an unknown supplier {row}")
        return "every child row links back to an assignment"

    check("no extra rows were added", no_extra_children)

    if failures:
        print(f"\n{len(failures)} check(s) failed.")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
