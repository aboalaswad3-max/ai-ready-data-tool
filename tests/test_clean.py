"""اختبارات أداة تجهيز البيانات — تعمل في أقل من ثانية."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clean import normalize_columns, fill_missing, drop_duplicates, read_rows, clean


def test_normalize_columns_lowercases_and_underscores():
    assert normalize_columns(["Order ID", "Unit Price", "Discount %"]) == [
        "order_id", "unit_price", "discount"
    ]


def test_fill_missing_mean_replaces_empty_numeric_cells():
    header = ["units"]
    rows = [["10"], [""], ["20"]]
    out = fill_missing(header, rows, "mean")
    assert out[1][0] == "15"


def test_fill_missing_drop_removes_incomplete_rows():
    header = ["units"]
    rows = [["10"], [""], ["20"]]
    assert fill_missing(header, rows, "drop") == [["10"], ["20"]]


def test_drop_duplicates_keeps_first_occurrence():
    rows = [["a", "1"], ["a", "1"], ["b", "2"]]
    assert drop_duplicates(rows) == [["a", "1"], ["b", "2"]]


def test_missing_input_file_does_not_crash():
    header, rows = read_rows("data/raw/does_not_exist.csv")
    assert header == [] and rows == []


def test_end_to_end_produces_output(tmp_path):
    src = tmp_path / "in.csv"
    src.write_text("Order ID,Units\n1,10\n2,\n", encoding="utf-8")
    dst = tmp_path / "out" / "clean.csv"
    stats = clean(str(src), str(dst), "mean")
    assert dst.exists()
    assert stats["rows_in"] == 2
