
import sqlite3
conn = sqlite3.connect('./data/matchstats.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM fd_matches WHERE league_code = 'CL'")
print(f"Total CL matches: {cursor.fetchone()[0]}")

cursor.execute("SELECT fd_id, home_team_name, away_team_name, status, match_date FROM fd_matches WHERE league_code = 'CL' ORDER BY match_date ASC LIMIT 10")
rows = cursor.fetchall()
for r in rows:
    print(dict(r))
conn.close()
