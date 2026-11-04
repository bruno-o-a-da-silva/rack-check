"""Steel, limits and beam profiles read from a TOML file. All values are illustrative."""

import tomllib
from dataclasses import dataclass
from decimal import Decimal
from importlib.resources import files
from pathlib import Path


@dataclass(frozen=True)
class Profile:
    name: str
    i_m4: float  # second moment of area
    w_m3: float  # elastic section modulus
    price: Decimal  # BRL per beam


@dataclass(frozen=True)
class Catalog:
    e_pa: float
    yield_pa: float
    deflection_ratio: float
    stress_factor: float
    profiles: dict[str, Profile]

    @property
    def allowed_stress_pa(self) -> float:
        return self.yield_pa / self.stress_factor


def load(path: Path | None = None) -> Catalog:
    if path is None:
        text = files("rack_check").joinpath("profiles.toml").read_text(encoding="utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    d = tomllib.loads(text)
    profiles = {
        name: Profile(name, p["i_mm4"] * 1e-12, p["w_mm3"] * 1e-9, Decimal(p["price_brl"]))
        for name, p in d["profiles"].items()
    }
    return Catalog(
        e_pa=d["steel"]["e_gpa"] * 1e9,
        yield_pa=d["steel"]["yield_mpa"] * 1e6,
        deflection_ratio=d["limits"]["deflection_ratio"],
        stress_factor=d["limits"]["stress_factor"],
        profiles=profiles,
    )
