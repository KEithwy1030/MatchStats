
import sqlite3
import datetime

db_path = "./data/matchstats.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

now_utc = datetime.datetime.now(datetime.timezone.utc)
today_str = now_utc.strftime('%Y-%m-%d')

print(f"Checking for CL matches on {today_str} UTC or nearby...")
cursor.execute("""
    SELECT fd_id, home_team_name, away_team_name, status, match_date 
    FROM fd_matches 
    WHERE league_code = 'CL' 
    AND (date(match_date) = ? OR date(match_date) = date(?, '+1 day') OR date(match_date) = date(?, '-1 day'))
    ORDER BY match_date ASC
""", (today_str, today_str, today_str))

rows = cursor.fetchall()
if not rows:
    print("No matches found for today/tomorrow in DB.")
    cursor.execute("SELECT max(match_date) FROM fd_matches WHERE league_code = 'CL'")
    print(f"Latest match date in DB for CL: {cursor.fetchone()[0]}")
else:
    for r in rows:
        print(f"[{r['status']}] {r['home_team_name']} vs {r['away_team_name']} @ {r['match_date']}")

conn.close()
