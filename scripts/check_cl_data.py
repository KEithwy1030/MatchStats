import sqlite3
import os
from datetime import datetime

db_path = "data/matchstats.db"

def check_cl_data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- CL Matches Check ---")
    cursor.execute("SELECT count(*) FROM fd_matches WHERE league_code = 'CL'")
    count = cursor.fetchone()[0]
    print(f"Total CL Matches: {count}")
    
    if count > 0:
        cursor.execute("SELECT match_date, home_team_name, away_team_name, status FROM fd_matches WHERE league_code = 'CL' ORDER BY match_date DESC LIMIT 5")
        for row in cursor.fetchall():
            print(row)

    print("\n--- Scorers Check (PL) ---")
    cursor.execute("SELECT count(*) FROM fd_scorers WHERE league_code = 'PL'")
    print(f"Total PL Scorers rows: {cursor.fetchone()[0]}")

    print("\n--- Scorers Check (CL) ---")
    cursor.execute("SELECT count(*) FROM fd_scorers WHERE league_code = 'CL'")
    print(f"Total CL Scorers rows: {cursor.fetchone()[0]}")

    conn.close()

if __name__ == "__main__":
    check_cl_data()
