"""Load CFTC Disaggregated COT (futures-only) into SQLite.

Reads:  data/cot_YYYY.zip (one per year, each containing f_year.txt)
Writes: data/cot.db -> cot_weekly(report_date, commodity, ...)

Keeps only CBOT corn and soybeans. Managed-money (hedge fund) positioning
is the headline series; commercials (Prod_Merc) and swaps kept for context.
"""
import csv
import io
import sqlite3
import zipfile
from pathlib import Path

DATA = Path("data")
DB = DATA / "cot.db"
YEARS = range(2020, 2027)

WANT = {
    "CORN - CHICAGO BOARD OF TRADE": "CORN",
    "SOYBEANS - CHICAGO BOARD OF TRADE": "SOYBEANS",
}

COLS = {
    "report_date": "Report_Date_as_YYYY-MM-DD",
    "open_interest": "Open_Interest_All",
    "prod_long": "Prod_Merc_Positions_Long_All",
    "prod_short": "Prod_Merc_Positions_Short_All",
    "swap_long": "Swap_Positions_Long_All",
    "swap_short": "Swap__Positions_Short_All",
    "mmoney_long": "M_Money_Positions_Long_All",
    "mmoney_short": "M_Money_Positions_Short_All",
    "other_long": "Other_Rept_Positions_Long_All",
    "other_short": "Other_Rept_Positions_Short_All",
}


def num(v):
    return int(v.strip().replace(",", "")) if v and v.strip() else 0


conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS cot_weekly")
cur.execute(
    """CREATE TABLE cot_weekly (
        report_date TEXT, commodity TEXT,
        open_interest INTEGER, prod_long INTEGER, prod_short INTEGER,
        swap_long INTEGER, swap_short INTEGER,
        mmoney_long INTEGER, mmoney_short INTEGER,
        other_long INTEGER, other_short INTEGER,
        PRIMARY KEY (report_date, commodity))"""
)

n = 0
for year in YEARS:
    zpath = DATA / f"cot_{year}.zip"
    with zipfile.ZipFile(zpath) as z:
        name = [i for i in z.namelist() if i.endswith(".txt")][0]
        text = io.TextIOWrapper(z.open(name), encoding="utf-8-sig")
        for row in csv.DictReader(text):
            market = row["Market_and_Exchange_Names"].strip()
            if market not in WANT:
                continue
            vals = {"commodity": WANT[market]}
            for k, col in COLS.items():
                vals[k] = row[col].strip() if k == "report_date" else num(row[col])
            cur.execute(
                """INSERT OR REPLACE INTO cot_weekly VALUES
                   (:report_date, :commodity, :open_interest, :prod_long, :prod_short,
                    :swap_long, :swap_short, :mmoney_long, :mmoney_short,
                    :other_long, :other_short)""",
                vals,
            )
            n += 1

conn.commit()
for r in cur.execute(
    "SELECT commodity, COUNT(*), MIN(report_date), MAX(report_date) "
    "FROM cot_weekly GROUP BY commodity"
):
    print(r)
conn.close()
print(f"done — {n} weekly reports in {DB}")
