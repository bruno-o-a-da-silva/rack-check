"""Safe load per rack level: the smaller of the sag limit and the stress limit.

A level is a pair of beams (front and back) carrying pallets spread along the span, so each
beam takes half the level load as a uniform load. Works on numpy arrays, one entry per level.
"""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from rack_check.catalog import Catalog

G = 9.81
Array = NDArray[np.float64]


def beam_limits(span: ArrayLike, i: ArrayLike, w: ArrayLike, cat: Catalog) -> tuple[Array, Array]:
    """Total uniform load in N one beam may carry before sag, and before stress, hits its limit.

    Sag: 5 W L^3 / (384 E I) = L / ratio  ->  W = 384 E I / (5 ratio L^2)
    Stress: W L / 8 / Wel = fy / factor     ->  W = 8 Wel fy / (factor L)
    """
    L = np.asarray(span, dtype=np.float64)
    if np.any(L <= 0):
        raise ValueError("spans must be positive")
    by_sag = 384.0 * cat.e_pa * np.asarray(i) / (5.0 * cat.deflection_ratio * L**2)
    by_stress = 8.0 * np.asarray(w) * cat.allowed_stress_pa / L
    return by_sag, by_stress


def level_capacity_kg(span: ArrayLike, i: ArrayLike, w: ArrayLike, cat: Catalog) -> Array:
    """Safe load of a beam pair in kg."""
    by_sag, by_stress = beam_limits(span, i, w, cat)
    return 2.0 * np.minimum(by_sag, by_stress) / G


def sag_mm(load_kg: ArrayLike, span: ArrayLike, i: ArrayLike, cat: Catalog) -> Array:
    """Sag of each beam of the pair under its half of the level load."""
    per_beam_n = np.asarray(load_kg, dtype=np.float64) * G / 2.0
    L = np.asarray(span, dtype=np.float64)
    return 5.0 * per_beam_n * L**3 / (384.0 * cat.e_pa * np.asarray(i)) * 1000.0
