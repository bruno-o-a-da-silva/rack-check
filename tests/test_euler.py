import pytest

from rack_check.euler import point_load, uniform_load

E = 200e9


def test_double_span_eight_sag() -> None:
    # carried over from the beam study
    a = point_load(1000, 1.0, 210e9, 8e-8, 8e-6)
    b = point_load(1000, 2.0, 210e9, 8e-8, 8e-6)
    assert b.deflection_m / a.deflection_m == pytest.approx(8.0)
    u = uniform_load(1000, 2.0, E, 1e-6, 2e-5)
    assert u.deflection_m / uniform_load(1000, 1.0, E, 1e-6, 2e-5).deflection_m == pytest.approx(8)


def test_hand_point_load() -> None:
    # derivation case 1: 10 kN at mid-span of 2.0 m, I = 1e-6, W = 2e-5
    b = point_load(10_000, 2.0, E, 1e-6, 2e-5)
    assert b.deflection_m == pytest.approx(10_000 * 8 / (48 * 200e9 * 1e-6))  # 8.333 mm
    assert b.stress_mpa == pytest.approx(250.0)


def test_spreading_the_load_cuts_sag_and_stress() -> None:
    p = point_load(10_000, 2.0, E, 1e-6, 2e-5)
    u = uniform_load(10_000, 2.0, E, 1e-6, 2e-5)
    assert u.deflection_m / p.deflection_m == pytest.approx(48 * 5 / 384)  # 0.625
    assert u.stress_mpa == pytest.approx(125.0)


@pytest.mark.parametrize("f", [point_load, uniform_load])
def test_rejects_non_positive(f: object) -> None:
    with pytest.raises(ValueError):
        f(0, 1.0, E, 1e-6, 2e-5)  # type: ignore[operator]
