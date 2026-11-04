"""Pass or fail for every rack level, and the cheapest beam that would make a failing one pass."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

import numpy as np

from rack_check.capacity import beam_limits, level_capacity_kg, sag_mm
from rack_check.catalog import Catalog


@dataclass(frozen=True)
class Level:
    bay: str
    level: int
    span_m: float
    profile: str
    pallets: int
    pallet_kg: float

    @property
    def load_kg(self) -> float:
        return self.pallets * self.pallet_kg


@dataclass(frozen=True)
class Result:
    level: Level
    capacity_kg: float
    utilisation: float
    sag_mm: float
    limit_mm: float
    governs: str  # "sag" or "stress"
    upgrade: str  # cheapest profile that passes, "" when the level passes or none does
    upgrade_cost: Decimal  # BRL for the beam pair

    @property
    def ok(self) -> bool:
        return self.utilisation <= 1.0


def check(levels: Sequence[Level], cat: Catalog) -> list[Result]:
    unknown = sorted({lv.profile for lv in levels} - cat.profiles.keys())
    if unknown:
        raise ValueError(f"unknown beam profiles: {', '.join(unknown)}")
    span = np.array([lv.span_m for lv in levels], dtype=np.float64)
    i = np.array([cat.profiles[lv.profile].i_m4 for lv in levels], dtype=np.float64)
    w = np.array([cat.profiles[lv.profile].w_m3 for lv in levels], dtype=np.float64)
    load = np.array([lv.load_kg for lv in levels], dtype=np.float64)
    cap = level_capacity_kg(span, i, w, cat)
    by_sag, by_stress = beam_limits(span, i, w, cat)
    sag = sag_mm(load, span, i, cat)
    out = []
    for k, lv in enumerate(levels):
        u = float(load[k] / cap[k])
        fix, cost = ("", Decimal("0.00")) if u <= 1.0 else cheapest_fix(lv, cat)
        out.append(
            Result(
                lv,
                float(cap[k]),
                u,
                float(sag[k]),
                lv.span_m / cat.deflection_ratio * 1000.0,
                "sag" if by_sag[k] <= by_stress[k] else "stress",
                fix,
                cost,
            )
        )
    return out


def cheapest_fix(lv: Level, cat: Catalog) -> tuple[str, Decimal]:
    """Cheapest profile whose beam pair carries the level load; ("", 0) if none does."""
    for p in sorted(cat.profiles.values(), key=lambda p: p.price):
        if float(level_capacity_kg(lv.span_m, p.i_m4, p.w_m3, cat)) >= lv.load_kg:
            return p.name, 2 * p.price
    return "", Decimal("0.00")


@dataclass(frozen=True)
class Summary:
    levels: int
    failing: int
    bays: int
    bays_over: list[str]
    no_fix: int  # failing levels no catalogue beam can carry: reduce the load instead
    fix_cost: Decimal


def summarise(results: Sequence[Result]) -> Summary:
    bad = [r for r in results if not r.ok]
    return Summary(
        levels=len(results),
        failing=len(bad),
        bays=len({r.level.bay for r in results}),
        bays_over=sorted({r.level.bay for r in bad}),
        no_fix=sum(1 for r in bad if not r.upgrade),
        fix_cost=sum((r.upgrade_cost for r in bad), Decimal("0.00")),
    )
