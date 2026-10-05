"""Attach a futures close to each COT report date.

COT positioning is reported as of Tuesday; this takes the futures settlement
on the Friday of that report week (report_date + 3 days, or the closest
trading day on/after it) so positioning can be plotted against price.

Reads:  ../corn-soy-futures-sql/data/futures.db  (daily_prices)
Writes: price_at_report(report_date, commodity, close) in data/cot.db
"""
import sqlite3
from datetime import date, timedelta

SYM = {"CORN": "ZC", "SOYBEANS": "ZS"}

fut = sqlite3.connect("../corn-soy-futures-sql/data/futures.db")
px = {  # (symbol, date) -> close
    (s, d): c
    for s, d, c in fut.execute("SELECT symbol, date, close FROM daily_prices")
}
fut.close()

conn = sqlite3.connect("data/cot.db")
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS price_at_report")
cur.execute(
    "CREATE TABLE price_at_report (report_date TEXT, commodity TEXT, close REAL,"
    " PRIMARY KEY (report_date, commodity))"
)

n = 0
for rep_date, comm in cur.execute(
    "SELECT report_date, commodity FROM cot_weekly"
).fetchall():
    sym = SYM[comm]
    d = date.fromisoformat(rep_date) + timedelta(days=3)  # Friday of report week
    for _ in range(7):  # walk forward to the next trading day
        key = (sym, d.isoformat())
        if key in px:
            cur.execute(
                "INSERT OR REPLACE INTO price_at_report VALUES (?,?,?)",
                (rep_date, comm, px[key]),
            )
            n += 1
            break
        d += timedelta(days=1)

conn.commit()
print(f"{n} report dates matched to a futures close")
print(cur.execute(
    "SELECT COUNT(*) FROM cot_weekly w LEFT JOIN price_at_report p "
    "USING (report_date, commodity) WHERE p.close IS NULL"
).fetchone(), "reports without a price")
conn.close()
