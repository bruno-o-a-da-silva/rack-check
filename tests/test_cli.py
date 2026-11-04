import runpy
from decimal import Decimal
from pathlib import Path

import pytest

from rack_check import synthetic
from rack_check.catalog import load
from rack_check.check import Level, check, summarise
from rack_check.cli import main
from rack_check.io import read_levels
from rack_check.report import render


def test_demo_numbers(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    html, csv, lv = tmp_path / "r.html", tmp_path / "r.csv", tmp_path / "l.csv"
    assert main(["demo", "--html", str(html), "--csv", str(csv), "--write", str(lv)]) == 0
    out = capsys.readouterr().out
    assert "48 bays, 192 levels" in out
    assert "bays over limit: 9 (B03, B09, C05, C06, D04, D05, D08, D09, D12)" in out
    assert "levels over limit: 17, of which no listed beam fits: 8" in out
    assert "beam pairs to replace: 9, illustrative cost BRL 5100.00" in out
    page = html.read_text(encoding="utf-8")
    assert "9 of 48 bays over their limit" in page and "qualified engineer" in page
    assert page.count('class="fail"') == 17
    assert csv.read_text(encoding="utf-8").count("FAIL") == 17
    assert read_levels(lv) == synthetic.site(4)


def test_check_own_file_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f = tmp_path / "l.csv"
    f.write_text(
        "bay,level,span_m,profile,pallets,pallet_kg\nX1,1,2.7,B100,2,1000\n", encoding="utf-8"
    )
    assert main(["check", str(f)]) == 0
    assert "bays over limit: 0 (none)" in capsys.readouterr().out
    f.write_text(
        "bay,level,span_m,profile,pallets,pallet_kg\nX1,1,2.7,B100,3,1000\n", encoding="utf-8"
    )
    assert main(["check", str(f)]) == 1


def test_report_escapes_and_no_fix_text() -> None:
    rs = check([Level("<b>", 1, 3.6, "B80", 3, 2000.0)], load())
    page = render(rs, summarise(rs))
    assert "&lt;b&gt;" in page and "reduce load" in page
    assert summarise(rs).fix_cost == Decimal("0.00")
    ok = check([Level("A", 1, 2.7, "B100", 1, 100.0)], load())
    assert "Bays over: none" in render(ok, summarise(ok))


def test_module_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["rack-check", "demo"])
    with pytest.raises(SystemExit) as e:
        runpy.run_module("rack_check", run_name="__main__")
    assert e.value.code == 0
