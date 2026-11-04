from decimal import Decimal
from pathlib import Path

import numpy as np
import pytest

from rack_check.capacity import G, beam_limits, level_capacity_kg, sag_mm
from rack_check.catalog import load
from rack_check.euler import uniform_load

CAT = load()
B100 = CAT.profiles["B100"]


def test_catalog() -> None:
    assert list(CAT.profiles) == ["B80", "B100", "B120", "B140"]
    assert B100.i_m4 == pytest.approx(1.2e-6) and B100.price == Decimal("230.00")
    assert CAT.allowed_stress_pa == pytest.approx(236.667e6, rel=1e-5)


def test_catalog_from_file(tmp_path: Path) -> None:
    text = (Path(__file__).parents[1] / "src/rack_check/profiles.toml").read_text()
    f = tmp_path / "p.toml"
    f.write_text(text.replace("e_gpa = 200.0", "e_gpa = 210.0"), encoding="utf-8")
    assert load(f).e_pa == pytest.approx(210e9)


def test_hand_b100_at_2700() -> None:
    # derivation case 2
    by_sag, by_stress = beam_limits(2.7, B100.i_m4, B100.w_m3, CAT)
    assert float(by_sag) == pytest.approx(12_642.0, abs=1.0)
    assert float(by_stress) == pytest.approx(16_830.0, abs=1.0)
    cap = float(level_capacity_kg(2.7, B100.i_m4, B100.w_m3, CAT))
    assert cap == pytest.approx(2 * 12_642.0 / G, abs=0.2)  # about 2,577 kg, sag governs
    # at that load each beam sags exactly span / 200 = 13.5 mm, matching the Euler core
    assert float(sag_mm(cap, 2.7, B100.i_m4, CAT)) == pytest.approx(13.5)
    b = uniform_load(cap * G / 2, 2.7, CAT.e_pa, B100.i_m4, B100.w_m3)
    assert b.deflection_m * 1000 == pytest.approx(13.5)


def test_vectorised_and_short_spans_turn_stress_governed() -> None:
    spans = np.array([1.0, 2.7, 3.6])
    by_sag, by_stress = beam_limits(spans, B100.i_m4, B100.w_m3, CAT)
    assert by_stress[0] < by_sag[0] and by_sag[2] < by_stress[2]


def test_bad_span() -> None:
    with pytest.raises(ValueError):
        level_capacity_kg([0.0], B100.i_m4, B100.w_m3, CAT)
