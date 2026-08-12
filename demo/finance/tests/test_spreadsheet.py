"""Spreadsheet ingestion — .xlsx and CSV, stdlib only.

SMEs keep books in Excel, so the app must read a real file rather than demand pasted CSV.
These tests build genuine .xlsx bytes (a ZIP of XML) and read them back, and pin the two
behaviours that protect a business's numbers: real-world column names and date formats are
recognised, and anything unreadable is REPORTED rather than guessed.
"""
import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from finance.spreadsheet import read_csv, read_table, read_xlsx, rows_to_dicts


def make_xlsx(rows: list[list[str]]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("xl/workbook.xml", "<workbook/>")
        body = []
        for r, row in enumerate(rows, 1):
            cells = "".join(
                f'<c r="{chr(64 + c)}{r}" t="inlineStr"><is><t>{v}</t></is></c>'
                for c, v in enumerate(row, 1))
            body.append(f'<row r="{r}">{cells}</row>')
        z.writestr("xl/worksheets/sheet1.xml",
                   '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org'
                   '/spreadsheetml/2006/main"><sheetData>' + "".join(body) + "</sheetData></worksheet>")
    return buf.getvalue()


def test_reads_a_real_xlsx_file():
    data = make_xlsx([["Date", "Amount"], ["2026-06-02", "125000"]])
    assert read_xlsx(data) == [["Date", "Amount"], ["2026-06-02", "125000"]]


def test_xlsx_is_detected_by_content_even_with_a_wrong_extension():
    data = make_xlsx([["Date"], ["2026-06-02"]])
    assert read_table("books.txt", data)[0] == ["Date"]


def test_header_names_are_normalised():
    rows = [["Value Date", "Narration ", "AMOUNT"], ["2026-06-02", "Sale", "125000"]]
    assert rows_to_dicts(rows)[0] == {"value_date": "2026-06-02", "narration": "Sale",
                                      "amount": "125000"}


def test_csv_delimiter_is_sniffed():
    assert read_csv("date;amount\n2026-06-02;125000\n")[1] == ["2026-06-02", "125000"]


def test_blank_rows_are_dropped():
    assert len(read_csv("date,amount\n\n2026-06-02,1\n")) == 2


@pytest.mark.parametrize("name,blob,expect", [
    ("statement.pdf", b"%PDF-1.4 ...", "PDF"),
    ("books.xls", b"\xd0\xcf\x11\xe0", ".xls"),
])
def test_unsupported_formats_fail_loudly_rather_than_guessing(name, blob, expect):
    """Silently mis-reading a bank statement would invent figures for someone's books."""
    with pytest.raises(ValueError, match=expect):
        read_table(name, blob)


def test_pdf_error_tells_the_operator_what_to_do_instead():
    with pytest.raises(ValueError, match="CSV or Excel"):
        read_table("s.pdf", b"%PDF-1.7")
