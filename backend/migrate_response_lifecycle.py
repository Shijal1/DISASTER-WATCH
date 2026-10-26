"""One-time migration: add response-lifecycle fields to alerts and incidents."""
import sqlite3
from pathlib import Path
DB = Path(__file__).parent / "data" / "disasterwatch.db"
con = sqlite3.connect(DB)
cur = con.cursor()
def add_column(table: str, column: str, ddl: str) -> None:
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    if column in existing:
        print(f"  {table}.{column} already exists")
        return
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
    print(f"  Added {table}.{column}")
print("Migrating alerts...")
add_column("alerts", "acknowledged_by", "TEXT")
add_column("alerts", "acknowledged_at", "DATETIME")
add_column("alerts", "escalation_level", "INTEGER DEFAULT 0")
print("Migrating incidents...")
add_column("incidents", "responding_at", "DATETIME")
add_column("incidents", "resolved_at", "DATETIME")
add_column("incidents", "acknowledged_by", "TEXT")
con.commit()
con.close()
print("Migration complete.")