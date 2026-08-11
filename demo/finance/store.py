"""Local SQLite store — the data spine of the offline financial intelligence stack.

Everything the analytics, anomaly, forecast and decision layers read comes from here.
No network, no server: one file on the operator's laptop.

MONEY IS STORED AS TEXT. SQLite has no decimal type and REAL would introduce binary
float error into money (0.1 + 0.2 != 0.3). We store the Decimal's string form and
rehydrate to Decimal on read, so every figure in the stack is exact.
"""
from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

TWO = Decimal("0.01")

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ref          TEXT,
    txn_date     TEXT NOT NULL,            -- ISO YYYY-MM-DD
    description  TEXT,
    amount       TEXT NOT NULL,            -- Decimal as string, always positive
    direction    TEXT NOT NULL CHECK (direction IN ('in','out')),
    category     TEXT,
    counterparty TEXT,
    UNIQUE (ref, txn_date, amount, direction)   -- re-importing a statement is idempotent
);
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id  TEXT PRIMARY KEY,
    customer    TEXT,
    amount      TEXT NOT NULL,
    issued_date TEXT NOT NULL,
    due_date    TEXT,
    paid        TEXT NOT NULL DEFAULT '0'
);
CREATE TABLE IF NOT EXISTS stock_movements (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sku        TEXT NOT NULL,
    description TEXT,
    move_date  TEXT NOT NULL,
    quantity   INTEGER NOT NULL,          -- always positive
    unit_cost  TEXT NOT NULL,             -- Decimal string; cost, not sale price
    direction  TEXT NOT NULL CHECK (direction IN ('in','out')),
    UNIQUE (sku, move_date, quantity, unit_cost, direction)
);
CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions (txn_date);
CREATE INDEX IF NOT EXISTS idx_txn_cat  ON transactions (category);
CREATE INDEX IF NOT EXISTS idx_stock_sku ON stock_movements (sku);
"""


def _d(x) -> Decimal:
    return Decimal(str(x)).quantize(TWO, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Txn:
    ref: str | None
    txn_date: date
    description: str
    amount: Decimal
    direction: str          # 'in' (money received) | 'out' (money spent)
    category: str | None
    counterparty: str | None


@dataclass(frozen=True)
class StockMove:
    """One movement of goods, valued at COST (never sale price) — this is the
    working-capital view of stock, not an operational stock-control record."""
    sku: str
    description: str
    move_date: date
    quantity: int
    unit_cost: Decimal
    direction: str          # 'in' = purchased into stock, 'out' = sold/consumed

    @property
    def value(self) -> Decimal:
        return _d(self.unit_cost * self.quantity)


@dataclass(frozen=True)
class InvoiceRow:
    invoice_id: str
    customer: str
    amount: Decimal
    issued_date: date
    due_date: date | None
    paid: Decimal

    @property
    def outstanding(self) -> Decimal:
        return _d(self.amount - self.paid)


def _as_date(v) -> date:
    if isinstance(v, date):
        return v
    return datetime.strptime(str(v).strip()[:10], "%Y-%m-%d").date()


class Store:
    """Business data on disk. Use `Store(':memory:')` in tests."""

    def __init__(self, path: str | Path = "business.db"):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ---- writes ----

    def add_transactions(self, rows) -> int:
        """Insert transactions; duplicates (same ref+date+amount+direction) are ignored,
        so re-importing an overlapping statement export never double-counts."""
        added = 0
        for t in rows:
            cur = self.conn.execute(
                "INSERT OR IGNORE INTO transactions "
                "(ref, txn_date, description, amount, direction, category, counterparty) "
                "VALUES (?,?,?,?,?,?,?)",
                (t.ref, t.txn_date.isoformat(), t.description, str(_d(t.amount)),
                 t.direction, t.category, t.counterparty))
            added += cur.rowcount
        self.conn.commit()
        return added

    def add_invoices(self, rows) -> int:
        added = 0
        for i in rows:
            cur = self.conn.execute(
                "INSERT OR REPLACE INTO invoices "
                "(invoice_id, customer, amount, issued_date, due_date, paid) VALUES (?,?,?,?,?,?)",
                (i.invoice_id, i.customer, str(_d(i.amount)), i.issued_date.isoformat(),
                 i.due_date.isoformat() if i.due_date else None, str(_d(i.paid))))
            added += cur.rowcount
        self.conn.commit()
        return added

    # ---- CSV ingestion (what the operator actually has) ----

    def import_transactions_csv(self, path: str | Path) -> int:
        """Import a transactions CSV. Expected headers (case-insensitive, flexible order):
        date, description, amount, direction, category, counterparty, ref
        `direction` may be omitted if amounts are signed (+in / -out)."""
        rows = []
        with open(path, newline="", encoding="utf-8") as fh:
            for raw in csv.DictReader(fh):
                r = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
                amt = Decimal(r["amount"].replace(",", "").replace("₦", "").replace("NGN", "").strip())
                direction = r.get("direction") or ("in" if amt >= 0 else "out")
                rows.append(Txn(
                    ref=r.get("ref") or None,
                    txn_date=_as_date(r["date"]),
                    description=r.get("description", ""),
                    amount=abs(amt),
                    direction=direction.lower(),
                    category=r.get("category") or None,
                    counterparty=r.get("counterparty") or None,
                ))
        return self.add_transactions(rows)

    def import_invoices_csv(self, path: str | Path) -> int:
        rows = []
        with open(path, newline="", encoding="utf-8") as fh:
            for raw in csv.DictReader(fh):
                r = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
                rows.append(InvoiceRow(
                    invoice_id=r["invoice_id"], customer=r.get("customer", ""),
                    amount=Decimal(r["amount"].replace(",", "")),
                    issued_date=_as_date(r["issued_date"]),
                    due_date=_as_date(r["due_date"]) if r.get("due_date") else None,
                    paid=Decimal((r.get("paid") or "0").replace(",", "")),
                ))
        return self.add_invoices(rows)

    # ---- reads ----

    def transactions(self, start: date | None = None, end: date | None = None,
                     direction: str | None = None) -> list[Txn]:
        sql = "SELECT * FROM transactions WHERE 1=1"
        args: list = []
        if start:
            sql += " AND txn_date >= ?"; args.append(start.isoformat())
        if end:
            sql += " AND txn_date <= ?"; args.append(end.isoformat())
        if direction:
            sql += " AND direction = ?"; args.append(direction)
        sql += " ORDER BY txn_date, id"
        return [Txn(r["ref"], _as_date(r["txn_date"]), r["description"], Decimal(r["amount"]),
                    r["direction"], r["category"], r["counterparty"])
                for r in self.conn.execute(sql, args)]

    def invoices(self, unpaid_only: bool = False) -> list[InvoiceRow]:
        rows = [InvoiceRow(r["invoice_id"], r["customer"], Decimal(r["amount"]),
                           _as_date(r["issued_date"]),
                           _as_date(r["due_date"]) if r["due_date"] else None,
                           Decimal(r["paid"]))
                for r in self.conn.execute("SELECT * FROM invoices ORDER BY issued_date")]
        return [i for i in rows if i.outstanding > 0] if unpaid_only else rows

    def add_stock_movements(self, rows) -> int:
        added = 0
        for m in rows:
            cur = self.conn.execute(
                "INSERT OR IGNORE INTO stock_movements "
                "(sku, description, move_date, quantity, unit_cost, direction) VALUES (?,?,?,?,?,?)",
                (m.sku, m.description, m.move_date.isoformat(), int(m.quantity),
                 str(_d(m.unit_cost)), m.direction))
            added += cur.rowcount
        self.conn.commit()
        return added

    def stock_movements(self, start: date | None = None, end: date | None = None,
                        direction: str | None = None) -> list[StockMove]:
        sql = "SELECT * FROM stock_movements WHERE 1=1"
        args: list = []
        if start:
            sql += " AND move_date >= ?"; args.append(start.isoformat())
        if end:
            sql += " AND move_date <= ?"; args.append(end.isoformat())
        if direction:
            sql += " AND direction = ?"; args.append(direction)
        sql += " ORDER BY move_date, id"
        return [StockMove(r["sku"], r["description"], _as_date(r["move_date"]), r["quantity"],
                          Decimal(r["unit_cost"]), r["direction"])
                for r in self.conn.execute(sql, args)]

    def has_stock_data(self) -> bool:
        return bool(self.conn.execute("SELECT 1 FROM stock_movements LIMIT 1").fetchone())

    def date_range(self) -> tuple[date, date] | None:
        r = self.conn.execute("SELECT MIN(txn_date) a, MAX(txn_date) b FROM transactions").fetchone()
        return (_as_date(r["a"]), _as_date(r["b"])) if r["a"] else None

    def close(self):
        self.conn.close()
