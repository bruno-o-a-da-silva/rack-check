"""Euler-Bernoulli bending of a simply supported beam.

`point_load` is the tested core carried over from the earlier `beam` study: one load at
mid-span. `uniform_load` spreads the same total load along the span, which is how pallets
sitting on a pair of rack beams are usually modelled.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Bending:
    deflection_m: float
    stress_mpa: float


def _check(*values: float) -> None:
    if min(values) <= 0:
        raise ValueError("load, span, stiffness and section must all be positive")


def point_load(p_n: float, span_m: float, e_pa: float, i_m4: float, w_m3: float) -> Bending:
    """Load P at mid-span: sag P L^3 / (48 E I), peak moment P L / 4."""
    _check(p_n, span_m, e_pa, i_m4, w_m3)
    delta = p_n * span_m**3 / (48.0 * e_pa * i_m4)
    return Bending(delta, p_n * span_m / 4.0 / w_m3 / 1e6)


def uniform_load(total_n: float, span_m: float, e_pa: float, i_m4: float, w_m3: float) -> Bending:
    """Total load W spread evenly: sag 5 W L^3 / (384 E I), peak moment W L / 8."""
    _check(total_n, span_m, e_pa, i_m4, w_m3)
    delta = 5.0 * total_n * span_m**3 / (384.0 * e_pa * i_m4)
    return Bending(delta, total_n * span_m / 8.0 / w_m3 / 1e6)
