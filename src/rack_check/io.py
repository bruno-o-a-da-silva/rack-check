"""CSV in and out for rack levels and their results."""

import csv
from collections.abc import Sequence
from pathlib import Path

from rack_check.check import Level, Result

FIELDS = ["bay", "level", "span_m", "profile", "pallets", "pallet_kg"]


def read_levels(path: Path) -> list[Level]:
    with path.open(newline="", encoding="utf-8") as f:
        return [
            Level(
                r["bay"],
                int(r["level"]),
                float(r["span_m"]),
                r["profile"],
                int(r["pallets"]),
                float(r["pallet_kg"]),
            )
            for r in csv.DictReader(f)
        ]


def write_levels(path: Path, levels: Sequence[Level]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for lv in levels:
            w.writerow([lv.bay, lv.level, lv.span_m, lv.profile, lv.pallets, f"{lv.pallet_kg:.0f}"])


def write_results(path: Path, results: Sequence[Result]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [*FIELDS, "load_kg", "capacity_kg", "utilisation", "sag_mm", "limit_mm", "governs"]
            + ["status", "upgrade", "upgrade_brl"]
        )
        for r in results:
            lv = r.level
            w.writerow(
                [lv.bay, lv.level, lv.span_m, lv.profile, lv.pallets, f"{lv.pallet_kg:.0f}"]
                + [f"{lv.load_kg:.0f}", f"{r.capacity_kg:.0f}", f"{r.utilisation:.3f}"]
                + [f"{r.sag_mm:.1f}", f"{r.limit_mm:.1f}", r.governs]
                + ["pass" if r.ok else "FAIL", r.upgrade, r.upgrade_cost]
            )
