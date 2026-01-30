
import sqlite3
import os

db_path = "./data/matchstats.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("Top 10 by Assists in DB (PL):")
cursor.execute("""
    SELECT player_name, goals, assists 
    FROM fd_scorers 
    WHERE league_code = 'PL' 
    AND id IN (
        SELECT MAX(id) FROM fd_scorers WHERE league_code = 'PL' GROUP BY player_id
    )
    ORDER BY assists DESC, goals DESC 
    LIMIT 10
""")
rows = cursor.fetchall()
for row in rows:
    print(f"{row['player_name']}: {row['assists']} Assists, {row['goals']} Goals")

conn.close()
