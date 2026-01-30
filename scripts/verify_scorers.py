
import sqlite3
import os

db_path = "./data/matchstats.db"
if not os.path.exists(db_path):
    print("DB not found")
else:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Checking scorers for PL:")
    cursor.execute("SELECT player_name, goals, assists FROM fd_scorers WHERE league_code = 'PL' ORDER BY goals DESC LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row['player_name']}: {row['goals']} Goals, {row['assists']} Assists")
    
    conn.close()
