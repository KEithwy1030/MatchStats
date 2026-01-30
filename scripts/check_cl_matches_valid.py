import sqlite3
import os

db_path = "data/matchstats.db"

def check_valid_cl_matches():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- CL Matches with Teams ---")
    # Check matches that actually have names
    cursor.execute("SELECT match_date, home_team_name, away_team_name, status FROM fd_matches WHERE league_code = 'CL' AND home_team_name IS NOT NULL LIMIT 5")
    rows = cursor.fetchall()
    if not rows:
        print("No CL matches with home_team_name found!")
    else:
        for row in rows:
            print(row)
            
    conn.close()

if __name__ == "__main__":
    check_valid_cl_matches()
