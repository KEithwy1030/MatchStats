
import sqlite3
import json

db_path = "./data/matchstats.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check for Jan 28/29 matches
cursor.execute("SELECT count(*) FROM fd_matches WHERE league_code = 'CL' AND match_date LIKE '2026-01-28%'")
c1 = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM fd_matches WHERE league_code = 'CL' AND match_date LIKE '2026-01-29%'")
c2 = cursor.fetchone()[0]

print(f"Matches for Jan 28: {c1}")
print(f"Matches for Jan 29: {c2}")

if c1 > 0 or c2 > 0:
    cursor.execute("SELECT home_team_name, away_team_name, status, match_date FROM fd_matches WHERE league_code = 'CL' AND (match_date LIKE '2026-01-28%' OR match_date LIKE '2026-01-29%') LIMIT 5")
    for r in cursor.fetchall():
        print(dict(r))

conn.close()
