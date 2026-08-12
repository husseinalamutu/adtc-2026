"""Read .xlsx and .csv without any third-party library.

SMEs keep their books in Excel, so "paste a CSV" is the wrong front door. An .xlsx file is
just a ZIP of XML parts, which the standard library can open — so we get real spreadsheet
support while keeping the engine dependency-free and fully offline (no CDN, no pip install,
nothing that could phone home with a business's books).

Scope: the sheet's used range as rows of strings, with the header row detected. Formatting,
formulas (we take the cached value), merged cells and multiple sheets beyond the first are
deliberately out of scope — this reads a transactions export, not arbitrary workbooks.
"""
from __future__ import annotations

import csv
import io
import re
import zipfile
from xml.etree import ElementTree

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_CELL_REF = re.compile(r"^([A-Z]+)(\d+)$")


def _col_index(ref: str) -> int:
    """'A' -> 0, 'B' -> 1, 'AA' -> 26. Needed because empty cells are simply absent from
    the XML, so position must come from the reference, not from order."""
    m = _CELL_REF.match(ref)
    letters = m.group(1) if m else ref
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def _shared_strings(zf: zipfile.ZipFile) -> list[str]:
    try:
        root = ElementTree.fromstring(zf.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    out = []
    for si in root.findall("m:si", NS):
        # a string may be split across several runs (<r><t>..</t></r>) when partly formatted
        out.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    return out


def _first_sheet_path(zf: zipfile.ZipFile) -> str:
    names = [n for n in zf.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
    if not names:
        raise ValueError("no worksheet found in this .xlsx file")
    return sorted(names)[0]


def read_xlsx(data: bytes) -> list[list[str]]:
    """Return the first worksheet as rows of strings (blank cells become '')."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise ValueError("this does not look like a valid .xlsx file") from None
    with zf:
        strings = _shared_strings(zf)
        root = ElementTree.fromstring(zf.read(_first_sheet_path(zf)))
        rows: list[list[str]] = []
        for row in root.iter(f"{{{NS['m']}}}row"):
            cells: dict[int, str] = {}
            for c in row.findall("m:c", NS):
                ref, ctype = c.get("r", ""), c.get("t", "n")
                if ctype == "inlineStr":
                    value = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
                else:
                    v = c.find("m:v", NS)
                    if v is None or v.text is None:
                        continue
                    value = strings[int(v.text)] if ctype == "s" and v.text.isdigit() \
                        and int(v.text) < len(strings) else v.text
                if value != "":
                    cells[_col_index(ref)] = value
            if cells:
                width = max(cells) + 1
                rows.append([cells.get(i, "") for i in range(width)])
    return rows


def read_csv(text: str) -> list[list[str]]:
    """Parse CSV/TSV, sniffing the delimiter so a semicolon or tab export also works."""
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    return [row for row in csv.reader(io.StringIO(text), dialect) if any(f.strip() for f in row)]


def read_table(filename: str, data: bytes) -> list[list[str]]:
    """Dispatch on the file's extension. Raises ValueError with an actionable message for
    anything we cannot read — notably PDF, where a wrong guess would silently invent a
    business's numbers."""
    name = (filename or "").lower()
    if name.endswith(".xlsx") or data[:2] == b"PK":
        return read_xlsx(data)
    if name.endswith((".csv", ".tsv", ".txt")):
        return read_csv(data.decode("utf-8", errors="replace"))
    if name.endswith(".pdf") or data[:4] == b"%PDF":
        raise ValueError(
            "PDF statements aren't supported yet — layouts vary too much between banks to "
            "read reliably, and guessing at your figures is not acceptable. Export as CSV "
            "or Excel from your bank/app, or paste the statement text into the "
            "reconciliation tab.")
    if name.endswith(".xls"):
        raise ValueError("legacy .xls isn't supported — re-save as .xlsx or CSV.")
    # last resort: it might still be delimited text
    try:
        return read_csv(data.decode("utf-8"))
    except UnicodeDecodeError:
        raise ValueError(f"cannot read {filename!r} — use CSV or Excel (.xlsx).") from None


def rows_to_dicts(rows: list[list[str]]) -> list[dict]:
    """Use the first non-empty row as the header, normalising names so 'Date', 'DATE' and
    'txn date' all land on the same key."""
    if not rows:
        return []
    header = [re.sub(r"[^a-z0-9]+", "_", h.strip().lower()).strip("_") for h in rows[0]]
    out = []
    for row in rows[1:]:
        record = {header[i]: (row[i] if i < len(row) else "")
                  for i in range(min(len(header), max(len(header), len(row))))
                  if i < len(header) and header[i]}
        if any(str(v).strip() for v in record.values()):
            out.append(record)
    return out
