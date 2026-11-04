"""Command line: `demo` on a synthetic site, `check` on your own CSV of rack levels."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from rack_check import catalog, synthetic
from rack_check.check import Level, Result, check, summarise
from rack_check.io import read_levels, write_levels, write_results
from rack_check.report import render


def run(levels: Sequence[Level], a: argparse.Namespace) -> list[Result]:
    results = check(levels, catalog.load(a.profiles))
    s = summarise(results)
    print(f"{s.bays} bays, {s.levels} levels")
    print(f"bays over limit: {len(s.bays_over)} ({', '.join(s.bays_over) or 'none'})")
    print(f"levels over limit: {s.failing}, of which no listed beam fits: {s.no_fix}")
    print(f"beam pairs to replace: {s.failing - s.no_fix}, illustrative cost BRL {s.fix_cost}")
    if a.html:
        a.html.write_text(render(results, s), encoding="utf-8")
    if a.csv:
        write_results(a.csv, results)
    return results


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="rack-check", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demo", help="synthetic site")
    d.add_argument("--seed", type=int, default=4)
    d.add_argument("--write", type=Path, help="also save the synthetic levels as CSV")
    c = sub.add_parser("check", help="CSV with bay,level,span_m,profile,pallets,pallet_kg")
    c.add_argument("levels", type=Path)
    for s in (d, c):
        s.add_argument("--profiles", type=Path, help="TOML of steel, limits and beams")
        s.add_argument("--html", type=Path, help="write the HTML report here")
        s.add_argument("--csv", type=Path, help="write the result table here")
    a = p.parse_args(argv)
    if a.cmd == "demo":
        levels = synthetic.site(a.seed)
        if a.write:
            write_levels(a.write, levels)
    else:
        levels = read_levels(a.levels)
    results = run(levels, a)
    return 1 if any(not r.ok for r in results) and a.cmd == "check" else 0
