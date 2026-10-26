import sqlite3
from pathlib import Path
db_path = Path(__file__).parent / "data" / "disasterwatch.db"
print(f"DB file: {db_path}")
print(f"Exists : {db_path.exists()}")
if db_path.exists():
    print(f"Size   : {db_path.stat().st_size} bytes\n")
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    count = cur.fetchone()[0]
    print(f"  {t:<15} {count} rows")
con.close()
