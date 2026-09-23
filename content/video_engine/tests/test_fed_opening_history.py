"""Strict data parsing; fixture values are synthetic and never production sources."""
import importlib.util
from pathlib import Path
from datetime import timedelta
from decimal import Decimal
import pytest

PATH = Path(__file__).resolve().parents[1] / "projects/systems-and-blowups/fed-liquidity-pressure/build_opening_history.py"
SPEC = importlib.util.spec_from_file_location("opening_history", PATH)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def rows():
    return [f"{M.START+timedelta(days=i*7)},1000000" for i in range((M.END-M.START).days//7+1)]


def payload(lines):
    return ("observation_date,WALCL\n"+"\n".join(lines)).encode()


def test_complete_wednesday_history_is_retained():
    result = M.observations(payload(rows()), "WALCL")
    assert len(result) == 159
    assert result[M.START] == Decimal("1000000")
    assert list(result)[-1] == M.END


@pytest.mark.parametrize("mutation", ["gap", "duplicate", "nan", "missing", "wrong_day"])
def test_bad_history_is_not_repaired(mutation):
    values = rows()
    if mutation == "gap":
        values.pop(30)
    elif mutation == "duplicate":
        values.append(values[30])
    elif mutation == "nan":
        values[30] = values[30].split(",")[0]+",NaN"
    elif mutation == "missing":
        values[30] = values[30].split(",")[0]+",."
    else:
        values[30] = f"{M.START+timedelta(days=30*7+1)},1000000"
    with pytest.raises(ValueError):
        M.observations(payload(values), "WALCL")


def test_leap_year_dates_are_calendar_correct():
    assert M.decimal_year(M.date(2024, 7, 2)) == 2024.5


def test_actual_archived_histories_match_published_rounded_changes():
    if not (M.DEFAULT_INTAKE / "MANIFEST.json").is_file():
        pytest.skip("raw FRED intake archive is not part of a clean checkout")
    result = M.build()
    assert result["readability"] == "landscape-phone"
    assert result["domain"] == [-2.5, 0.5]
    assert "from_zero" not in result
    assert all(result["domain"][0] <= point[1] <= result["domain"][1]
               for series in result["series"] for point in series["pts"])
    assert result["facts"]["endpoint_changes_usd_billions"] == {
        "WALCL": "-2237.895", "WRBWFRBL": "72.28"}
    assert [s["pts"][0][1] for s in result["series"]] == [0, 0]
    assert [s["pts"][-1][1] for s in result["series"]] == [-2.237895, 0.07228]
    assert all(len(s["pts"]) == 159 for s in result["series"])
    assert result["facts"]["interpolation"] is False
    assert result["facts"]["decimation"] is False


def test_archive_hash_mismatch_is_blocking(tmp_path):
    raw = tmp_path / "source.csv"
    raw.write_text("test", encoding="utf-8")
    entry = {"path": str(raw), "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=WALCL",
             "sha256": "0"*64, "bytes": 4}
    with pytest.raises(ValueError, match="hash/byte count"):
        M.verified_entry(tmp_path, {"entries": [entry]}, raw.name)
