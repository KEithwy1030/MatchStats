import sqlite3
import os

db_path = "data/matchstats.db"

def check_data():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- Standings Data ---")
    cursor.execute("SELECT league_code, season, count(*) FROM fd_standings GROUP BY league_code, season")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Scorers Data ---")
    cursor.execute("SELECT league_code, season, count(*) FROM fd_scorers GROUP BY league_code, season")
    for row in cursor.fetchall():
        print(row)

    print("\n--- Teams Data Sample ---")
    cursor.execute("SELECT fd_id, name, name_cn FROM fd_teams LIMIT 5")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    check_data()
