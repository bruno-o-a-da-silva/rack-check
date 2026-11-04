from decimal import Decimal

import pytest

from rack_check.catalog import load
from rack_check.check import Level, cheapest_fix, check, summarise

CAT = load()


def test_hand_levels() -> None:
    # derivation case 3: B100 at 2.7 m carries about 2,577 kg per level
    ok = Level("A01", 1, 2.7, "B100", 2, 1000.0)
    over = Level("A01", 2, 2.7, "B100", 3, 1000.0)
    r = check([ok, over], CAT)
    assert r[0].ok and r[0].utilisation == pytest.approx(2000 / 2577.4, rel=1e-3)
    assert r[0].limit_mm == pytest.approx(13.5) and r[0].governs == "sag"
    assert r[0].sag_mm == pytest.approx(13.5 * 2000 / 2577.4, rel=1e-3)
    assert not r[1].ok and r[1].upgrade == "B120" and r[1].upgrade_cost == Decimal("580.00")
    assert r[0].upgrade == "" and r[0].upgrade_cost == Decimal("0.00")


def test_short_span_stress_governs() -> None:
    assert check([Level("B", 1, 1.0, "B80", 1, 100.0)], CAT)[0].governs == "stress"


def test_no_fix_and_summary() -> None:
    huge = Level("C02", 1, 3.6, "B80", 3, 2000.0)
    assert cheapest_fix(huge, CAT) == ("", Decimal("0.00"))
    rs = check([huge, Level("C01", 1, 2.7, "B100", 2, 1000.0)], CAT)
    s = summarise(rs)
    assert (s.levels, s.failing, s.bays, s.bays_over, s.no_fix) == (2, 1, 2, ["C02"], 1)
    assert s.fix_cost == Decimal("0.00")


def test_unknown_profile() -> None:
    with pytest.raises(ValueError, match="B999"):
        check([Level("A", 1, 2.7, "B999", 1, 1.0)], CAT)
