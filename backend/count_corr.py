import sqlite3
con = sqlite3.connect(r"C:\Users\Lenovo\Desktop\disasterwatch\backend\data\disasterwatch.db")
cur = con.cursor()
cur.execute("SELECT COUNT(*) FROM incidents WHERE source='correlation'")
print("correlation incidents:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM incidents WHERE source='citizen' AND latitude BETWEEN 19 AND 20")
print("Mumbai citizen incidents:", cur.fetchone()[0])
cur.execute("SELECT incident_id, latitude, longitude, location_name FROM incidents WHERE source='correlation'")
for row in cur.fetchall():
    print(row)
con.close()
